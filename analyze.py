#!/usr/bin/python3

import os
import timeit
import subprocess

# timeout in seconds
TIMEOUT = 5

# Format for res-data:
# 1. auto_end | killed
# 2. Time it took in seconds
# 3. Output of command (if any). May be on several lines after this line as well.

def runCmd(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, timeout=TIMEOUT).stdout.decode('utf-8')

parserLocation = "/home/gustav/kod/miner-ray.github.io/Parser/parser.js"
#samplesLocation = "/home/gustav/kod/dataset/wat-filtered"
#resDataLocation = "./res-data"

samplesLocation = "/home/gustav/kod/dataset/wat-wasm-evasion-selected"
resDataLocation = "./res-data-wasm-evasion"

i = 0

for sampleFilename in os.listdir(samplesLocation):
    sampleFile = os.path.join(samplesLocation, sampleFilename)
    if not os.path.isfile(sampleFile):
        continue

    dataFileName = os.path.splitext(sampleFilename)[0] + '.txt'
    dataFile = os.path.join(resDataLocation, dataFileName)

    if os.path.isfile(dataFile):
        print('Result file already exists for ' + sampleFile + ', skipping...')
        continue

    print(sampleFile)

    # record start time
    t_0 = timeit.default_timer()

    exitType = 'auto_end'
    res = None

    # run miner-ray
    try:
        res = runCmd(['node', parserLocation, '-f', sampleFile])
    except subprocess.TimeoutExpired:
        exitType = 'killed'

    # record end time
    t_1 = timeit.default_timer()
    elapsed_time = round((t_1 - t_0), 3)

    print(res)

    resFile = open(dataFile, "w")
    resFile.write(exitType + '\n')
    resFile.write(str(elapsed_time) + '\n')
    if res != None:
        resFile.write(res + '\n')
    resFile.close()

    i += 1
    if i >= 35:
        break
