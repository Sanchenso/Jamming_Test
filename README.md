# Jamming_Test
scanning logs GNSS for jamming detection

this script use the georinex lib (https://github.com/geospace-code/georinex/releases) and use the parser.
The script must be in the folder with the parser and the drone log.

detect_jemming_test
argument 1 - number of drone
argument 2 - min SNR (dBHz)
argument 3 - number of satellites

If the number of sattelites is less then 'argument 3' with the selected SNR 'argument 2' in each of the navigation systems (GPS or GLONASS) in the drone log (argument 1), print "detect" and create a text file with the time of jamming detection.

example of using:
python3 detect_jemming_test.py 63 25 3

In drone 63 number of satellite 3 (minimum 3 satillete of GPS or minimum 3 satillete of GLONASS) with SNR 25 dBHz and above.

If it is needed, few logs could be scanning. Add detect_jemming_all.py in folder and use it.
Warning - than script starting, all files .txt, .ubx, .obs in the folder will be removed!

detect_jemming_all.py
argument 1 - min SNR (dBHz)
argument 2 - number of satellites

example of using:
python3 detect_jemming_test.py 25 3

In all logs drones in folder number of satellite 3 (minimum 3 satillete of GPS or minimum 3 satillete of GLONASS) with SNR 25 dBHz and above.
