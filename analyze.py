#!/usr/bin/python3

import os
import timeit
import subprocess
import sqlite3
import argparse
import sys
import json 

# connect to db
dbCon = sqlite3.connect("data.db")
dbCur = dbCon.cursor()

parserLocation = "/home/gustav/kod/miner-ray.github.io/Parser/parser.js"
samplesLocation = "/home/gustav/kod/dataset/filtered"
tmpWatLocation = "./tmp-wat"

parser=argparse.ArgumentParser()

parser.add_argument("--skip", help="Skip processing existing entries in DB", action="store_true")
parser.add_argument("--convert-timeout", help="Timeout for the conversion in seconds, default is 5")
parser.add_argument("--ray-timeout", help="Timeout for the miner-ray parser in seconds, default is 5")

args=parser.parse_args()

# Default values for arguments:
SKIP = False
CONVERT_TIMEOUT = 5
RAY_TIMEOUT = 5

# Check supplied arguments and possible overwrite default ones:
if args.skip:
    SKIP = True
if args.convert_timeout != None:
    CONVERT_TIMEOUT = int(args.convert_timeout)
if args.ray_timeout != None:
    RAY_TIMEOUT = int(args.ray_timeout)

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
        unlikely        INTEGER
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

def processFile(id):
    print(f"Processing {id}...")

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
   
    res = runCmd(['wasm2wat', wasmFilePath], CONVERT_TIMEOUT)
    dbCur.execute('UPDATE data SET convert_status=?, convert_time=? WHERE id=?', [res[0], res[1], id])
    dbCon.commit()

    if res[0] < 2:
        print(f"Conversion ended with timeout/error ({res[0]}).")
        return
    
    resFile = open(watFilePath, "w")
    resFile.write(res[2])
    resFile.close()

    # Now, do the ray parsing:
    (resStatus, t, data) = runCmd(['node', parserLocation, '-f', watFilePath], RAY_TIMEOUT)

    # Delete the wat-file:
    os.remove(watFilePath)

    # If resStatus indicates success (2) but data says it's an error, set resStatus to error
    if resStatus == 2:
        if "error" in json.loads(data):
            resStatus = 1 # set to error

    dbCur.execute('UPDATE data SET ray_status=?, ray_time=? WHERE id=?', [resStatus, t, id])
    dbCon.commit()

    if resStatus < 2:
        print(f"Parsing ended with timeout/error ({resStatus}).")
        return

    insertRayDataToDB(id, data)
    print("Parsing ended with success")


#
# MAIN CODE
#

createTable()

i = 0

for sampleFilename in os.listdir(samplesLocation):
    sampleFile = os.path.join(samplesLocation, sampleFilename)

    if not os.path.isfile(sampleFile):
        continue

    id = os.path.splitext(sampleFilename)[0]

    processFile(id)

    i += 1

    if i >= 10:
        break
