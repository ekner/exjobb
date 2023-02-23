#!/usr/bin/python3

import os
import timeit
import subprocess

# timeout in seconds
TIMEOUT = 30

# Format for res-data:
# 1. auto_end | killed
# 2. Time it took in seconds
# 3. Output of command (if any). May be on several lines after this line as well.

def runCmd(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, timeout=TIMEOUT).stdout.decode('utf-8')

parserLocation = "/home/gustav/kod/miner-ray.github.io/Parser/parser.js"
samplesLocation = "/home/gustav/kod/samples-wasm-bench/chosen-wat"
resDataLocation = "/home/gustav/kod/ray-runner/res-data"

i = 0

for filename in os.listdir(samplesLocation):
    f = os.path.join(samplesLocation, filename)
    if not os.path.isfile(f):
        continue

    i += 1

    dataF = os.path.splitext(f)[0] + '.txt'

    if os.path.isfile(dataF):
        print('Result file already exists for ' + f + ', skipping...')
        continue

    print(f)

    # record start time
    t_0 = timeit.default_timer()

    exitType = 'auto_end'
    res = None

    # run miner-ray
    try:
        res = runCmd(['node', parserLocation, '-f', f])
    except subprocess.TimeoutExpired:
        exitType = 'killed'

    # record end time
    t_1 = timeit.default_timer()
    elapsed_time = round((t_1 - t_0), 3)

    print(res)

    resFile = open(dataF, "w")
    resFile.write(exitType)
    resFile.write(elapsed_time)
    resFile.write(res)
    resFile.close()

    i += 1
    if i == 3:
        break
