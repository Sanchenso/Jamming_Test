import subprocess
import os
import sys
import time

path = os.listdir()
arg2 = sys.argv[1]
arg3 = sys.argv[2]

folder_name = 'Results'  # Папка для вывода результатов
if not os.path.exists(folder_name):
    os.mkdir(folder_name)

for k in os.listdir(os.path.join(os.getcwd(), folder_name)): #  зачищаем папку перед началом
    os.remove(os.path.join(os.getcwd(), folder_name, k))

for k in path: # удаляем лишнее
    if k[-4:] == '.obs' or k[-4:] == '.ubx':
        print(k)
        os.remove(k)
path = os.listdir()
def check():
    while True:
        print('please entry y on n')
        iin = str(input())
        if iin == 'y' or iin == 'n':
            return iin


print('Do you need to change number of drones?')
iin = check()

numberLog = 0
allNumberLog = 0

for logs in path:
    if logs[-4:] == '.bin':
        allNumberLog += 1

if iin == 'n':
    start = time.time()
    '''Если не нужно переименовывать файлы'''
    for i in path:
        if i[-4:] == '.bin':
            numberLog += 1
            print(i)
            print(numberLog, 'of', allNumberLog)
            subprocess.call("python3 detect_jemming_test.py " + i + " " + arg2 + " " + arg3, shell=True)

elif iin == 'y':
    print('You sure? This is inversible, please make copy of logs')
    print('Renumber now?')
    iin = check()
    start = time.time()
    if iin == 'y':
        '''Если нужно переименовывать файлы'''
        oldName = {}
        path = os.listdir()
        for i in path:
            if i[-4:] == '.bin':
                os.rename(i, '1_' + i)
                oldName['1_' + i] = None
        with open(os.path.join(os.getcwd(), folder_name, 'newNameDrones.txt'), 'w') as f:
            for j in sorted(oldName.keys()):
                numberLog += 1
                newName = str(numberLog) + '.bin'
                oldName[j] = newName
                f.write(str(newName))
                f.write(' ')
                f.write(str(j)[2:])
                f.write('\n')
                os.rename(j, newName)
                print(newName)
                print(numberLog, 'of', allNumberLog)
                subprocess.call("python3 detect_jemming_test.py " + newName + " " + arg2 + " " + arg3, shell=True)
            f.close()
        print('pls check the file: newNameDrones.txt')
    else:
        print('repeat a function call')
    print('Working time:', end=' ')
print(time.time() - start, 'sec')
