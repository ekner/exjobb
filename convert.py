#!/usr/bin/python3

import os
import subprocess

# Format for meta-data:
# 1. success | fail
# 2. Time it took in seconds
# 3. Output of command (if any). May be on several lines after this line as well.

def runCmd(cmd):
    tmp = subprocess.run(cmd, stdout=subprocess.PIPE)
    tmp.check_returncode()
    return tmp.stdout.decode('utf-8')

src = "/home/gustav/kod/dataset/filtered"
dest = "/home/gustav/kod/dataset/wat-filtered"

#src = "/home/gustav/kod/dataset/wasm-evasion-selected"
#dest = "/home/gustav/kod/dataset/wat-wasm-evasion-selected"

#metaData = "./convertMetaData"

i = 0

for filename in os.listdir(src):
    f = os.path.join(src, filename)
    if not os.path.isfile(f):
        continue

    i += 1

    # Check if this file already is converted:
    destF = os.path.join(dest, filename)
    destF = os.path.splitext(destF)[0] + '.wat'
    if os.path.isfile(destF):
        print("dest already exists!")
        continue

    if filename != "6f688eecc5197f61a99ad766a162496bfdea6abc84742d1c417ba72b43a63534.wasm":
        continue

    print('File number ' + str(i))
    print('Source: ' + f)
    print('Dest: ' + destF)

    res = ""
    try:
        res = runCmd(['wasm2wat', f])
    except:
        print("Exception!!!!!!")
    
    resFile = open(destF, "w")
    resFile.write(res)
    resFile.close()
    
    if i >= 1:
        break
