Scanning GNSS logs for jamming detection

On Windows, you need to use the convbin version b34f, available at this link (https://github.com/geospace-code/georinex/releases). The script must be in the folder with convbin.exe and the receiver log.

Required Arguments:

1. argument 1 - name of the log file.
2. argument 2 - minimum SNR (dBHz).
3. argument 3 - number of satellites.

Optional Arguments:

- --system - name of the system (e.g., GPS).
- --band - band identifier of the system (e.g., L1).
- --archive - if specified, archives the folder (use with folder)
- --folder - if need to repalce log in folder
- --plot - if specified, shows the plot.
- --start_delay - delay time for start of processing, sec (e.g., 30)
- --stop_delay  - delay time for stop of processing, sec (e.g., 30)
- --time - time of processing, onsidering start and stop delay, sec (e.g., 30)


Functionality:

If the number of satellites is less than 'argument 3' at the specified SNR ('argument 2') in any of the navigation systems (GPS, GLONASS, BeiDou) in the drone log ('argument 1'), the script will print "warning" and create a text file with the time of the problem.
Graph saving and display is also supported.

Usage Examples:

- On Linux: ```python3 detect_jamming_test.py test_NEO_M8.ubx 30 5```
- On Windows (PowerShell): ```python .\detect_jamming_test.py .\test_NEO_M8.ubx 30 5```

For *log test_NEO_M8.ubx*, a minimum of 5 satellites (either GPS or GLONASS) with an SNR of 30 dBHz and above is required.

To specify only one system, for example, GPS L1, and to show the plot and archive. 
Log is cut off from the beginning to 30 seconds and at the end to 30 seconds:
```python3 detect_jamming_test.py test_NEO_M8.ubx 30 5 --system GPS --band L1 --plot --folder --archive --start_delay 30 --stop_delay 30```

Log is cut off from the beginning to 30 seconds and duration is 30 from the of cutting :
```python3 detect_jamming_test.py test_NEO_M8.ubx 30 5 --system GPS --band L1 --plot --start_delay 30 --time 30```

## detect_jamming_all.py - processing with a single command
example of usage:
```python3 detect_jamming_all.py```


Put this script in the directory with detect_jamming_test.py and it will process all the files in the folder according to the specified parameters:
```
config = {
    "start_delay": 60,
    "time": 120,
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
```
The parameters can be changed manually.
