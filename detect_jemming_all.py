import os
import subprocess
import sys

files = os.listdir()
min_snr = sys.argv[1]
min_sats = sys.argv[2]
target_system = sys.argv[3] if len(sys.argv) > 3 else ""
target_band = sys.argv[4] if len(sys.argv) > 4 else ""

for i in files:
    if i.endswith(('.dat', '.ubx', '.log', '.cyno')):
        print(i)

        command = f"python3 detect_jamming_test.py {i} {min_snr} {min_sats}"
        if target_system:
            command += f" {target_system}"
        if target_band:
            command += f" {target_band}"

        subprocess.call(command, shell=True)
