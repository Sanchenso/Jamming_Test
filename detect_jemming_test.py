import georinex as gr
import os
import sys
import subprocess
from datetime import datetime
from matplotlib.pyplot import figure, show, savefig

ax = figure().gca()

arg = sys.argv[1]  # наименование лога дрона
arg2 = sys.argv[2]  # значение SNR
arg3 = sys.argv[3]  # значение кол-ва спутников

if arg[-4:] == ".bin" or arg[-4:] == ".ubx":
    index = arg.index('.')
    arg = arg[:index]

binFile = arg + ".bin"
ubxFile = arg + ".ubx"
obsFile = arg + ".obs"

try:
    subprocess.call("./parser --raw_data " + binFile, shell=True)
    os.remove(arg + "_channel_lua_125.dat")
    os.remove(arg + "_channel_passports_124.dat")
    os.remove(arg + "_channel_telemetry_123.dat")
    os.remove(arg + "_flight_0.gscl")
    os.remove(arg + "_flight_0.params")
except Exception:
    print(binFile, " are not parsing!")

try:
    os.rename(arg + "_channel_gnss_126.dat", ubxFile)
except Exception:
    print("no file 126.dat")

subprocess.call("convbin " + ubxFile + " -o " + obsFile + " -os -r ubx", shell=True)
hdr = gr.rinexheader(obsFile)
# print(hdr.get('fields'))  # вывод типа данных нав. систем

obsG = gr.load(obsFile, use=['G'])
obsR = gr.load(obsFile, use=['R'])

# fullTime = min(obsG['S1C'].time.values.size, obsR['S1C'].time.values.size)  # определение временного диапазона

if obsR['S1C'].time.values.size < obsG['S1C'].time.values.size:
    b = obsR['S1C'].time.values.size  # определяем длину временного отрезок
else:
    b = obsG['S1C'].time.values.size
print(b)

# spisok_name_satG = list((obsG['S1'].sv.values))				# формируем список всех спутников GPS
# spisok_name_satR = list((obsR['S1'].sv.values))				# формируем список всех спутников GLONASS
ng = 0
nr = 0
l = 0

for j in range(b):  # проверка на кол-во спутников с заданным SNR
    l += 1
    for k in obsG['S1C'][j].values:
        if k > int(arg2):
            ng += 1
    for m in obsR['S1C'][j].values:
        if m > int(arg2):
            nr += 1
    if ng < int(arg3) and nr < int(arg3):
        print('detect')
        time_jam = str(obsG['S1C'][j].time.values)
        time_jam_convert = datetime.fromisoformat(time_jam[0:-3])
        print(datetime.strftime(time_jam_convert, '%H:%M:%S'))
        # with open('data_jemming_' + arg + '.csv', 'a') as f:
        with open('data_jemming_all.csv', 'a') as f:
            f.write(arg)
            f.write(' ')
            f.write(str(datetime.strftime(time_jam_convert, '%H:%M:%S')))
            f.write('\n')
        f.close()
    ng = 0
    nr = 0

if l < b:  # проверка на потерянные данные
    print('error -', end=' ')
    print(b - l, end=' (')
    print(round(((b - l) * 100) / b), end=' %)')
# ax.plot(obsG.time, obsG['S1'], label = spisok_name_satG)		# строим графики SNR для всех спутников GPS
# ax.legend()
# show()
# ax.plot(obsR.time, obsR['S1'], label = spisok_name_satR)		# строим графики SNR для всех спутников GLONASS
# ax.legend()
# show()
