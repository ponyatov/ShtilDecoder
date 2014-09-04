# -*- coding: cp1251 -*-
# Декодер файлов Штиля №2

import os,sys,time,re

DATDIR = 'dat/3'
DATFILEMASK = '%s/374ШИМП_%i (%i)(K).dat'

# выходной файл лога
LOG=open('log.log','w')

# генерация набора имен файлов и загрузка в словарь
DAT={} # словарь
RECS = 0 # счетчик максимального числа строк в .dat файлах
for i in [1,2]:
    for j in range(1,12+1):
        DatFileName=DATFILEMASK%(DATDIR,i,j)
        print DatFileName
        F=open(DatFileName) # открываем файл
        # читаем файл в виде списка строк
        # применяя лябда-функцию получающую 1ый столбец (бит)
        # (нумерация в списках начинается с нуля)
        # функция split([X]) делит строку по разделителю и возвращает список
        # split() делит по пробельным символам
        DATLIST=F.readlines()
        RECS=max(RECS,len(DATLIST))
        DAT[(i,j)]=map(lambda x:x.split()[1],DATLIST) 
        F.close() # закрываем файл

# каналы
K1=[]
K2=[]
K3=[]
for r in range(RECS):
    K1.append('%.2X'%int('%c%c%c%c%c%c%c%c'%(
          DAT[(1,1)][r],
          DAT[(1,2)][r],
          DAT[(1,3)][r],
          DAT[(1,4)][r],
          DAT[(1,5)][r],
          DAT[(1,6)][r],
          DAT[(1,7)][r],
          DAT[(1,8)][r],
          ),2)
    )
    K2.append('%c%c%c%c%c%c%c%c'%(
          DAT[(1,9)][r],
          DAT[(1,10)][r],
          DAT[(1,11)][r],
          DAT[(1,12)][r],
          DAT[(2,1)][r],
          DAT[(2,2)][r],
          DAT[(2,3)][r],
          DAT[(2,4)][r],
          )
    )
    K3.append('%c%c%c%c%c%c%c%c'%(
          DAT[(2,5)][r],
          DAT[(2,6)][r],
          DAT[(2,7)][r],
          DAT[(2,8)][r],
          DAT[(2,9)][r],
          DAT[(2,10)][r],
          DAT[(2,11)][r],
          DAT[(2,12)][r],
          )
    )

print >>LOG,'Ch1\n'
N=0
for i in K1:
    print >>LOG,i,
    N+=1
    if not N%0x10: print >>LOG

LOG.close()