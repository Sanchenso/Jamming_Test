# Jamming_Test
scanning logs GNSS for jamming detection

this script use the georinex lib (https://github.com/geospace-code/georinex/releases) and use the parser.
The script must be in the folder with the parser and the drone log.

detect_jemming_test
argument 1 - number of drone
argument 2 - min SNR (dBHz)
argument 3 - number of satellites

If there are numer of sattelites is less then 'argument 3' with the selected SNR 'argument 2' in each of the navigation system (GPS or GLONASS) in the drone log (argument 1), print "detect" and create a text file with the time of jamming detection.

example of using:
python3 detect_jemming_test.py 63 25 3

In drone 63 number of satellite 3 (3 of GPS or 3 of GLONASS) with min SNR 25 dBHz.

If it is needed, few logs could be scanning. 
Warning - than script starting, all .txt, .ubx, .obs in the folder will be removed!

detect_jemming_all.py
argument 1 - min SNR (dBHz)
argument 2 - number of satellites
