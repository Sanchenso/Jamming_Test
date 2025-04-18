Scanning GNSS logs for jamming detection

On Windows, you need to use the convbin version b34f, available at this link (https://github.com/geospace-code/georinex/releases). The script must be in the folder with convbin.exe and the receiver log.

Required Arguments:

1. argument 1 - name of the log file.
2. argument 2 - minimum SNR (dBHz).
3. argument 3 - number of satellites.

Optional Arguments:

- --system (not necessary) - name of the system (e.g., GPS).
- --band (not necessary) - band identifier of the system (e.g., L1).
- --archive (not necessary) - if specified, archives the folder.
- --plot (not necessary) - if specified, shows the plot.

Functionality:

If the number of satellites is less than 'argument 3' at the specified SNR ('argument 2') in any of the navigation systems (GPS, GLONASS, BeiDou) in the drone log ('argument 1'), the script will print "warning" and create a text file with the time of the problem.
Graph saving and display is also supported.

Usage Examples:

- On Linux: ```python3 detect_jamming_test.py test_NEO_M8.ubx 30 5```
- On Windows (PowerShell): ```python .\detect_jamming_test.py .\test_NEO_M8.ubx 30 5```

For *log test_NEO_M8.ubx*, a minimum of 5 satellites (either GPS or GLONASS) with an SNR of 30 dBHz and above is required.

To specify only one system, for example, GPS L1, and to show the plot and archive:
```python3 detect_jamming_test.py test_NEO_M8.ubx 30 5 --system GPS --band L1 --plot --archive```
