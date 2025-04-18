# Jamming_Test
scanning logs GNSS for jamming detection

On windows need to use use the convbin version b34f [https://github.com/geospace-code/georinex/releases](https://github.com/rtklibexplorer/RTKLIB/releases/tag/b34f)
The script must be in the folder with the convbin.exe and the receiver log.

argument 1 - number of drone;

argument 2 - min SNR (dBHz);

argument 3 - number of satellites.

argument 4 (not nessesuary) - name of System

argument 5 (not nessesuary)  -  name of System ID



If the number of sattelites is less then 'argument 3' with the selected SNR 'argument 2' in each of the navigation systems (GPS or GLONASS) in the drone log (argument 1), print "detect" and create a text file with the time of jamming detection.

example of using linux:
python3 detect_jemming_test.py test_ZED_F9.ubx 25 3

example of using windows (power shell):
python .\detect_jamming_test.py .\test_ZED_F9.ubx 25 5 

In drone №63 number of satellite  is 3 (minimum 3 satillete of GPS or minimum 3 satillete of GLONASS) with SNR 25 dBHz and above.

If need only one system, for example GPS L1: 
python3 detect_jemming_test.py test_ZED_F9.ubx 25 3 GPS L1
