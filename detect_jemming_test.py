import georinex as gr
import os
import sys
import subprocess
from matplotlib.pyplot import figure, show, savefig

ax = figure().gca()

arg = sys.argv[1]												 # номер дрона

binFile = arg + ".bin"
ubxFile = arg + ".ubx"
obsFile = arg + ".obs"

subprocess.call("./parser --raw_data " + binFile, shell=True)

os.remove(arg + ".txt")											# удаляем текстовый файл с параметрами автопилота
os.remove(arg + ".gscl")
#os.remove(arg + "_channel_123.dat")
os.rename(arg + "_channel_126.dat", ubxFile)

arg2 = sys.argv[2]												# значение SNR
arg3 = sys.argv[3]												# значение кол-ва спутников

subprocess.call("convbin " + ubxFile + " -o " + obsFile + " -os -r ubx", shell=True)

obsG = gr.load(obsFile, use=['G'])	
obsR = gr.load(obsFile, use=['R'])
b = obsG['S1'].time.values.size 				    			# определяем длину временного отрезок

#spisok_name_satG = list((obsG['S1'].sv.values))				# формируем список всех спутников GPS
#spisok_name_satR = list((obsR['S1'].sv.values))				# формируем список всех спутников GLONASS
ng = 0
nr = 0
l = 0
for j in range(b):												# проверка на кол-во спутников с заданным SNR
	l += 1
	for k in obsG['S1'][j].values:							
		if k > int(arg2):
			ng += 1
	for m in obsR['S1'][j].values:	
		if m > int(arg2):
			nr += 1
	if ng < int(arg3) and nr < int(arg3):
		print('detect')
		print(obsG['S1'][j].time.values)
		time_jam = obsG['S1'][j].time.values
		with open('data_jemming_' + arg + '.txt','a') as f:
			f.write('Drone: ' + arg)
			f.write(' ')
			f.write('Time: ' + str(time_jam))
			f.write('\n')
		f.close()
	ng = 0
	nr = 0

if l < b:														# проверка на потерянные данные 
	print('error -', end = ' ')
	print(b - l, end = ' (')
	print(round(((b-l)*100)/b), end = ' %)')
#ax.plot(obsG.time, obsG['S1'], label = spisok_name_satG)		# строим графики SNR для всех спутников GPS
#ax.legend()	
#show()
#ax.plot(obsR.time, obsR['S1'], label = spisok_name_satR)		# строим графики SNR для всех спутников GLONASS
#ax.legend()									
#show()
