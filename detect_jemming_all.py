import subprocess
import os
import sys
import time
path = os.listdir()
arg2 = sys.argv[1]
arg3 = sys.argv[2]
for k in path:
    if k[-4:] == '.obs' or k[-4:] == '.ubx' or k[-4:] == '.txt':
        print(k)
        os.remove(k)

for i in path:
    if i[-4:] == '.bin':
        binFile = i[:-4]
        print(binFile)
        subprocess.call("python3 detect_jemming_test.py " + binFile + " " + arg2 + " " + arg3, shell=True)
time.sleep(3)
for l in path:
    if l[-4:] == '.obs' or l[-4:] == '.ubx' or l[-4:] == '.txt':
        print(l)
        os.remove(l)