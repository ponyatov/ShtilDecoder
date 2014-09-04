# -*- coding: cp1251 -*-
# Декодер файлов Штиля №2

import os,sys,time,re

# выходной файл лога
LOG=open('log.log','w')

def dump(L):
    '''
    функция вывода дампа по 0x10 элементов    
    '''
    T=''
    N=0
    for i in L:
        if not N%0x10: T+='\n%.4X\t'%N # каждые 0x10 элементов выводим адрес
        N+=1
        T+='%s '%i
    return '%s\n'%T
        
class Channel:
    '''
    класс канала
    '''
    def __init__(self, id):
        self.id=id
        self.dat=[]
    def __str__(self):
        ' текстовое представление объекта '
        T='\n%s\nКанал #%s длина %i байт\n%s'%('='*60,self.id,len(self),'-'*60)
        T+=dump(self.dat[:0x20])+'...\n'+'='*60
        return T
    def append(self,item):
        ' добавление элемента '
        self.dat+=[item]
    def __len__(self):
        ' число элементов объекта '
        return len(self.dat)
    def __getitem__(self,index):
        ' получение элемента '
        return self.dat[index]

class Frame:
    '''
    класс пакета
    '''
    def __init__(self,ch,addr,dat):
        self.ch=ch
        self.addr=addr
        self.dat=dat
        # декодирование
        self.signature=dat[0:2+1]
        self.blockN=dat[3]
        self.time=dat[4:7+1]
        self.BSKVU1=dat[8:11+1]
        self.BSKVU2=dat[12:15+1]
        self.DM1peak=dat[16:20+1]
        self.DM2peak=dat[21:25+1]
        self.Temp=dat[26:29+1]
        self.CRC_H=dat[30]
        self.CRC_L=dat[31]
    def __str__(self):
        T='\n%s\nканал %i кадр @%.4X\n%s'%('='*60,self.ch,self.addr,'-'*60)
        T+=dump(self.dat)+'-'*60
        T+='\nсигнатура:\t\t%s'%self.signature
        T+='\n№ блока:\t\t%s'%self.blockN
        T+='\nвремя Штыря:\t%s'%self.time
        T+='\nБСКВУ1:\t\t\t%s'%self.BSKVU1
        T+='\nБСКВУ2:\t\t\t%s'%self.BSKVU2
        T+='\nПик DM1:\t\t%s'%self.DM1peak
        T+='\nПик DM2:\t\t%s'%self.DM2peak
        T+='\nТемпература:\t%s'%self.Temp
        T+='\nCRC_H:\t\t\t%s'%self.CRC_H
        T+='\nCLC_L:\t\t\t%s'%self.CRC_L
        return T+'\n'+'='*60     
    
class DataDir:
    '''
    генерация набора имен файлов и загрузка в словарь
    выполняется в конструкторе при создании объекта
    '''
    # маска имени файла
    DATFILEMASK = '%s/374ШИМП_%i (%i)(K).dat'
    def __init__(self,D):
        print >>LOG,self,D
        # каналы
        self.K1,self.K2,self.K3=Channel(1),Channel(2),Channel(3)
        self.DATDIR=D
        self.DAT={} # словарь
        self.RECS = 0 # счетчик максимального числа строк в .dat файлах
        self.LoadFromFiles()
        self.FillData()
        self.FindPackages()
    def LoadFromFiles(self):
        ' загрузка данных из файлов '
        self.FILES={} # список длин файлов с данными в порядке загрузки
        for i in [1,2]:
            for j in range(1,12+1):
                # генерация имени .dat-файла по маске
                DatFileName=self.DATFILEMASK%(self.DATDIR,i,j)
                # открываем файл
                F=open(DatFileName) 
                # читаем файл в виде списка строк
                DATLIST=F.readlines()
                self.FILES[DatFileName]=len(DATLIST)
                # обновление максимума длины файлов
                self.RECS=max(self.RECS,self.FILES[DatFileName])
                print >>LOG,'%s: %i строк'%(DatFileName,self.FILES[DatFileName])
                # применяя к списку лябда-функцию получающую 1ый столбец (бит)
                # (нумерация в списках начинается с нуля)
                # функция split([X]) делит строку по разделителю 
                # и возвращает список
                # split() делит по пробельным символам
                self.DAT[(i,j)]=map(lambda x:x.split()[1],DATLIST)
                # закрываем файл 
                F.close()
    def FindPackages(self):
        ' сканирование на маркеры пакетов '
        for K in [self.K1,self.K2,self.K3]:
            print >>LOG,K
            for i in range(len(K)-31):
                if K[i:i+2]==['55','AA']:
                    print >>LOG,Frame(1,i-1,K[i-1:i+31])
    def FillData(self):
        ' заполнение каналов данными '
        X={# разбитовка каналов
           #        0      1      2      3      4      5      6      7
           self.K1:[(1,1 ),(1,2 ),(1,3 ),(1,4 ),(1,5 ),(1,6 ),(1,7 ),(1,8 )],
           self.K2:[(1,9 ),(1,10),(1,11),(1,12),(2,1 ),(2,2 ),(2,3 ),(2,4 )],
           self.K3:[(2,5 ),(2,6 ),(2,7 ),(2,8 ),(2,9 ),(2,10),(2,11),(2,11)]
           }
        for r in range(self.RECS):
            for K in X:
                K.append('%.2X'%int('%c%c%c%c%c%c%c%c'%(
                    self.DAT[(X[K][0][0],X[K][0][1])][r],
                    self.DAT[(X[K][1][0],X[K][1][1])][r],
                    self.DAT[(X[K][2][0],X[K][2][1])][r],
                    self.DAT[(X[K][3][0],X[K][3][1])][r],
                    self.DAT[(X[K][4][0],X[K][4][1])][r],
                    self.DAT[(X[K][5][0],X[K][5][1])][r],
                    self.DAT[(X[K][6][0],X[K][6][1])][r],
                    self.DAT[(X[K][7][0],X[K][7][1])][r],
                ),2))

for D in ['dat/1','dat/2','dat/3']:
    DataDir(D)
    
LOG.close()
