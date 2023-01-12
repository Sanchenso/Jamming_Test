import georinex as gr
import os
import sys
import subprocess
from matplotlib.pyplot import figure, show, savefig
from numpy import timedelta64

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

folder_name = 'Results' # Папка для вывода результатов
if not os.path.exists(folder_name):
    os.mkdir(folder_name)

'''skip parser if only UBX'''
try:
    subprocess.call("./parser --raw_data " + binFile, shell=True)
    os.remove(arg + ".txt")  # удаляем текстовый файл с параметрами автопилота
    os.remove(arg + ".gscl")
    os.remove(arg + "_channel_123.dat")
except Exception:
    pass
try:
    os.rename(arg + "_channel_126.dat", ubxFile)
except Exception:
    pass

subprocess.call("convbin " + ubxFile + " -o " + obsFile + " -os -r ubx", shell=True)
hdr = gr.rinexheader(obsFile)
# print(hdr.get('fields')) # вывод типа данных нав. систем

obsG = gr.load(obsFile, use=['G'])
obsR = gr.load(obsFile, use=['R'])

fullTime = min(obsG['S1'].time.values.size, obsR['S1'].time.values.size)  # определение временного диапазона

timeDeltaG = timedelta64(obsG['S1'].time[fullTime - 1].values - obsG['S1'].time[0].values, 's')
timeDeltaR = timedelta64(obsR['S1'].time[fullTime - 1].values - obsR['S1'].time[0].values, 's')

# spisok_name_satG = list((obsG['S1'].sv.values))				# формируем список всех спутников GPS
# spisok_name_satR = list((obsR['S1'].sv.values))				# формируем список всех спутников GLONASS
ng = 0
nr = 0
schet = 0
for j in range(fullTime):  # проверка на кол-во спутников с заданным SNR
    schet += 1
    for k in obsG['S1'][j].values:
        if k > int(arg2):
            ng += 1
    for m in obsR['S1'][j].values:
        if m > int(arg2):
            nr += 1
    if ng < int(arg3) and nr < int(arg3):
        print('detect')
        time_jam = str(obsG['S1'][j].time.values)[11:22]
        print(time_jam)
        with open(os.path.join(os.getcwd(), folder_name, 'data_jemming_all.csv'), 'a') as f:
            f.write(time_jam)
            f.write(' ')
            f.write(arg)
            f.write('\n')
        f.close()
    ng = 0
    nr = 0
with open(os.path.join(os.getcwd(), folder_name, 'data_propuski.csv'), 'a') as f2:
    propuski = int(str(timeDeltaG*5 - fullTime)[:-8])
    percent_propuski = round(((propuski) * 100) / fullTime)
    print(fullTime, propuski, percent_propuski, end='% \n')
    f2.write(arg + ' ' + str(fullTime) + ' ' + str(propuski) + ' ' + str(percent_propuski) + '%')
    f2.write('\n')


# ax.plot(obsG.time, obsG['S1'], label = spisok_name_satG)		# строим графики SNR для всех спутников GPS
# ax.legend()
# show()
# ax.plot(obsR.time, obsR['S1'], label = spisok_name_satR)		# строим графики SNR для всех спутников GLONASS
# ax.legend()
# show()
