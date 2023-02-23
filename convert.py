#!/usr/bin/python3

import os
import subprocess

def runCmd(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')

src = "/home/gustav/kod/samples-wasm-bench/chosen"
dest = "/home/gustav/kod/samples-wasm-bench/chosen-wat"

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

    print('Source: ' + f)
    print('Dest: ' + destF)
    res = runCmd(['wasm2wat', f])
    
    resFile = open(destF, "w")
    resFile.write(res)
    resFile.close()
    
    if i == 100:
        break
