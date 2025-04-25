import os
import subprocess
import sys

files = os.listdir()

snr_GPS_L1 = 30
nSat_GPS_L1 = 5
snr_Glonass_L1 = 30
nSat_Glonass_L1 = 5
snr_BeiDou_L1 = 30
nSat_BeiDou_L1 = 5

snr_GPS_L2 = 30
nSat_GPS_L2 = 5
snr_Glonass_L2 = 30
nSat_Glonass_L2 = 5
snr_BeiDou_L2 = 30
nSat_BeiDou_L2 = 5

for i in files:
    if i.endswith(('.dat', '.ubx', '.log', '.cyno')):
        print(i)
        command = f"python3 detect_jamming_test.py {i} 30 5 --system GPS --band L1 --start_delay 60 --time 120"
        subprocess.call(command, shell=True)
        command = f"python3 detect_jamming_test.py {i} 30 5 --system GPS --band L2 --start_delay 60 --time 120"
        subprocess.call(command, shell=True)
        command = f"python3 detect_jamming_test.py {i} 30 5 --system BeiDou --band L1 --start_delay 60 --time 120"
        subprocess.call(command, shell=True)
        command = f"python3 detect_jamming_test.py {i} 30 5 --system BeiDou --band L2 --start_delay 60 --time 120"
        subprocess.call(command, shell=True)
        command = f"python3 detect_jamming_test.py {i} 30 5 --system Glonass --band L1 --start_delay 60 --time 120"
        subprocess.call(command, shell=True)
        command = f"python3 detect_jamming_test.py {i} 30 5 --system Glonass --band L2  --start_delay 60 --time 120 --folder --archive"
        subprocess.call(command, shell=True)

