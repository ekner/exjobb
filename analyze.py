#!/usr/bin/python3

import os
import timeit
import subprocess
import sqlite3
import argparse
import json
from obfuscator import obfuscateFile
from pynput import keyboard

# connect to db
dbCon = sqlite3.connect("data.db")
dbCur = dbCon.cursor()

parserLocation = "/home/gustav/kod/miner-ray.github.io/Parser/parser.js"
#samplesLocation = "/home/gustav/kod/dataset/filtered"
#samplesLocation = "/home/gustav/kod/dataset/filtered-miners"
samplesLocation = "/home/gustav/kod/dataset/non-miners-213"
tmpWatLocation = "./tmp-wat"
obfuscatorPath = "/home/gustav/kod/exjobb/obfuscator.py"

parser=argparse.ArgumentParser()

parser.add_argument("--skip", help="Skip processing existing entries in DB", action="store_true")
parser.add_argument("--convert-timeout", help="Timeout for the conversion in seconds")
parser.add_argument("--ray-timeout", help="Timeout for the miner-ray parser in seconds")
parser.add_argument("--max-count", help="Maximum amount of files to process, 0 means unlimited (default)")
parser.add_argument("--id", help="Run for individual ID only")

args=parser.parse_args()

# Default values for arguments:
SKIP = True
CONVERT_TIMEOUT = 5
RAY_TIMEOUT = 20
MAX_COUNT = 0
ONLY_ID = None

# Check supplied arguments and possible overwrite default ones:
if args.skip:
    SKIP = True
if args.convert_timeout != None:
    CONVERT_TIMEOUT = int(args.convert_timeout)
if args.ray_timeout != None:
    RAY_TIMEOUT = int(args.ray_timeout)
if args.max_count != None:
    MAX_COUNT = int(args.max_count)
if args.id != None:
    ONLY_ID = args.id

# Constants:
obfuscations = ["s5"]

# --------- #
# FUNCTIONS #
# --------- #

def getElapsedTime(t0):
    t1 = timeit.default_timer()
    return round((t1 - t0), 3)

# Returns tuples (returnType, totalTime, data)
# returnType 0 == timeout
# returnType 1 == error
# returnType 2 == success
def runCmd(cmd, timeout):
    # record start time
    t0 = timeit.default_timer()

    tmp = None
    try:
        tmp = subprocess.run(cmd, stdout=subprocess.PIPE, timeout=timeout)
        tmp.check_returncode()
    except subprocess.TimeoutExpired:
        elapsedTime = getElapsedTime(t0)
        return (0, elapsedTime, None)
    except:
        elapsedTime = getElapsedTime(t0)
        return (1, elapsedTime, None)

    elapsedTime = getElapsedTime(t0)
    return (2, elapsedTime, tmp.stdout.decode('utf-8'))

def createTable():
    print("Creating table...")
    sql = """
    CREATE TABLE IF NOT EXISTS data (
        id              TEXT,
        convert_status  INTEGER,
        ray_status      INTEGER,
        convert_time    INTEGER,
        ray_time        INTEGER,
        data            TEXT,
        certain         INTEGER,
        probable        INTEGER,
        unlikely        INTEGER,
        linesAdded      INTEGER,
        linesRemoved    INTEGER,
        linesBefore     INTEGER,
        newFileSize     INTEGER,
        oldFileSize     INTEGER,
        matches         INTEGER
    );"""
    res = dbCur.execute(sql)
    print(res)

def insertRayDataToDB(id, res):
    data = json.loads(res)

    certainLen = 0
    probableLen = 0
    unlikelyLen = 0

    if "certain" in data:
        certainLen = len(data["certain"])
    if "probable" in data:
        probableLen = len(data["probable"])
    if "unlikely" in data:
        unlikelyLen = len(data["unlikely"])

    values = [res, certainLen, probableLen, unlikelyLen, id]
    dbCur.execute('UPDATE data SET data=?, certain=?, probable=?, unlikely=? WHERE id=?', values)
    dbCon.commit()

def obfuscate(watFilePath, id):
    # Convert to wasm before obfuscation to get file size. We cannot read the original wasm file size because
    # it might be larger, so we have to go Wasm -> Wat -> Wasm first.
    res = runCmd(['wat2wasm', watFilePath], 20)
    fileSize = os.stat(f"{id}.wasm").st_size
    dbCur.execute('UPDATE data SET oldFileSize=? WHERE id=?', [fileSize, id])
    dbCon.commit()

    # Perform the obfuscations:
    stat = obfuscateFile(watFilePath, obfuscations)
    
    # Try to convert back to wasm:
    res = runCmd(['wat2wasm', watFilePath], 20)
    print("Convert back to wasm: " + str(res))

    # Get file size:
    fileSize = os.stat(f"{id}.wasm").st_size

    # Remove the leftoverfile from conversion:
    os.remove(f"{id}.wasm")

    # Store results in DB:
    dbCur.execute('UPDATE data SET linesAdded=?, linesRemoved=?, linesBefore=?, matches=?, newFileSize=? WHERE id=?',
                  [stat["linesAdded"], stat["linesRemoved"], stat["linesBefore"], stat["matches"], fileSize, id])
    dbCon.commit()

def processFile(id):
    dbEntry = dbCur.execute('SELECT * FROM data WHERE id=?', [id])
    res = dbEntry.fetchone()

    if res != None and SKIP:
        print(f"Entry exists in db, skipping...")
        return

    # If the entry didn't exists, create an empty one now:
    if res == None:
        dbCur.execute('INSERT INTO data (id) VALUES (?)', [id])
        dbCon.commit()

    wasmFileName = f"{id}.wasm"
    wasmFilePath = os.path.join(samplesLocation, wasmFileName)
    watFileName = f"{id}.wat"
    watFilePath = os.path.join(tmpWatLocation, watFileName)
   
    # Convert the file and store the results:
    res = runCmd(['wasm2wat', wasmFilePath], CONVERT_TIMEOUT)
    dbCur.execute('UPDATE data SET convert_status=?, convert_time=? WHERE id=?', [res[0], res[1], id])
    dbCon.commit()

    if res[0] < 2:
        print(f"Conversion ended with timeout/error ({res[0]}).")
        return

    print("Conversion ended with success")
    
    resFile = open(watFilePath, "w")
    resFile.write(res[2])
    resFile.close()

    # Perform obfuscation (if it should be performed):
    obfuscate(watFilePath, id)

    # Now, do the ray parsing:
    (resStatus, t, data) = runCmd(['node', parserLocation, '-f', watFilePath], RAY_TIMEOUT)

    # Delete the wat-file:
    os.remove(watFilePath)

    # If resStatus indicates success (2), check that it actually succeeded by looking at the data:
    if resStatus == 2:
        try:
            jsonData = json.loads(data)
            if "error" in jsonData:
                resStatus = 1 # set to error
        except:
            # We cannot even parse the json data, so set to error:
            resStatus = 1

    dbCur.execute('UPDATE data SET ray_status=?, ray_time=? WHERE id=?', [resStatus, t, id])
    dbCon.commit()

    if resStatus < 2:
        print(f"Parsing ended with timeout/error ({resStatus}).")
        return

    insertRayDataToDB(id, data)
    print("Parsing ended with success")

def handler(key):
    global stopLoop
    if key == keyboard.Key.esc:
        stopLoop = True
        print("Esc key pressed, will stop after this one...")
        return False

#
# MAIN CODE
#

listener = keyboard.Listener(on_press=handler)
listener.start()

createTable()

if ONLY_ID != None:
    print('Processing individual file...')
    processFile(ONLY_ID)
    exit(0)

i = 0
fileIndex = 0
stopLoop = False

for sampleFilename in os.listdir(samplesLocation):
    sampleFile = os.path.join(samplesLocation, sampleFilename)

    if not os.path.isfile(sampleFile):
        continue

    fileIndex += 1

    id = os.path.splitext(sampleFilename)[0]

    print(f"File: {fileIndex}, Scanned: {i}, Name: {id}")

    processFile(id)

    i += 1

    if MAX_COUNT > 0 and i >= MAX_COUNT:
        print("Stopped because max-count was reached")
        break
    if stopLoop:
        print("Stopped because Esc was pressed")
        break
