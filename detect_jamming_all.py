import os
import subprocess

files = os.listdir()

config = {
    "start_delay": 60,
    "time": 120,
    "archive": True,
    "systems": {
        "GPS": {
            "L1": {"snr": 35, "sats": 7},
            "L2": {"snr": 31, "sats": 5}
        },
        "Glonass": {
            "L1": {"snr": 35, "sats": 7},
            "L2": {"snr": 30, "sats": 5}
        },
        "BeiDou": {
            "L1": {"snr": 30, "sats": 5},
            "L2": {"snr": 30, "sats": 5}
        }
    }
}


for i in files:
    if i.endswith(('.dat', '.ubx', '.log', '.cyno')):
        print(i)
        command = f'python3 detect_jamming.py {i} {config["systems"]["GPS"]["L1"]["snr"]} {config["systems"]["GPS"]["L1"]["sats"]} --system GPS --band L1 --start_delay {config["start_delay"]} --time {config["time"]}'
        print(command)
        subprocess.call(command, shell=True)
        command = f'python3 detect_jamming.py {i} {config["systems"]["GPS"]["L2"]["snr"]} {config["systems"]["GPS"]["L2"]["sats"]} --system GPS --band L2 --start_delay {config["start_delay"]} --time {config["time"]}'
        print(command)
        subprocess.call(command, shell=True)
        command = f'python3 detect_jamming.py {i} {config["systems"]["Glonass"]["L1"]["snr"]} {config["systems"]["Glonass"]["L1"]["sats"]} --system Glonass --band L1 --start_delay {config["start_delay"]} --time {config["time"]}'
        print(command)
        subprocess.call(command, shell=True)
        command = f'python3 detect_jamming.py {i} {config["systems"]["Glonass"]["L2"]["snr"]} {config["systems"]["Glonass"]["L2"]["sats"]} --system Glonass --band L2 --start_delay {config["start_delay"]} --time {config["time"]}'
        print(command)
        subprocess.call(command, shell=True)
        command = f'python3 detect_jamming.py {i} {config["systems"]["BeiDou"]["L1"]["snr"]} {config["systems"]["BeiDou"]["L1"]["sats"]} --system BeiDou --band L1 --start_delay {config["start_delay"]} --time {config["time"]}'
        print(command)
        subprocess.call(command, shell=True)
        command = f'python3 detect_jamming.py {i} {config["systems"]["BeiDou"]["L2"]["snr"]} {config["systems"]["BeiDou"]["L2"]["sats"]} --system BeiDou --band L2 --start_delay {config["start_delay"]} --time {config["time"]} --folder --archive'
        print(command)
        subprocess.call(command, shell=True)