# -*- coding: cp1251 -*-
# Декодер файлов Штыря №2
######################################################

# каталог с данными
DATDIR='dat/3' 

# маска имени файла
DATFILEMASK = '%s/374ШИМП_%i (%i)(K).dat'

CHBT={
# разбитовка каналов: байт 76543210
#        0      1      2      3      4      5      6      7
'K1':[(1,8 ),(1,7 ),(1,6 ),(1,5 ),(1,4 ),(1,3 ),(1,2 ),(1,1 )],
'K2':[(2,4 ),(2,3 ),(2,2 ),(2,1 ),(1,12),(1,11),(1,10),(1,9 )],
'K3':[(2,12),(2,11),(2,10),(2,9 ),(2,8 ),(2,7 ),(2,6 ),(2,5 )]
}

# выходной файл с таблицей, открывать в Excel или браузере
HTML1 = open('%s/kadr1.html'%DATDIR,'w')

######################################################

import os,sys,time,re,math

# выходной файл лога
sys.stdout=open('log.log','w')

print >>HTML1,'<html><title>%s</title>'%DATDIR

print time.localtime()[:6],sys.argv
print '\nDATDIR "%s"\n'%DATDIR
print 'DATFILEMASK "%s"\n'%DATFILEMASK

def dump(dat):
    'функция вывода кекс-дампа'
    T=''
    for addr in range(len(dat)):
        if addr%0x10==0: T+='\n%.4X\t'%addr
        T+='%.2X '%dat[addr]
    return T

############################

class Channel:
    '1-битный канал'
    def __init__(self,i,j):
        # генерация имени .dat-файлов по маске
        self.i=i; self.j=j
        self.DatFileName = DATFILEMASK%(DATDIR,i,j)
        # чтение файла
        DatFile = open(self.DatFileName)
        Records = DatFile.readlines()
        DatFile.close()
        # генерация списка битов
        self.dat = map(lambda x:int(x.split()[1]),Records)
    def __str__(self):
        return 'Канал %i:%i\t%s\t[%i]'%(\
            self.i,self.j,\
            self.DatFileName,\
            len(self))
    def __len__(self): return len(self.dat)
    def __getitem__(self,idx): return self.dat[idx]

# загрузка каналов из файлов

DAT={}
for i in [1,2]:
    for j in range(1,12+1):
        DAT[(i,j)]=Channel(i,j)
        print DAT[(i,j)] 

############################

class ByteStream:
    'поток байтовых данных'
    def __init__(self,ID,BT):
        self.ID=ID
        self.BT=BT
        self.DAT=[]
        self.SZ=len(DAT[(1,1)])
        for i in range(self.SZ):
            byte=0
            for bit in range(8):
                byte=byte*2+DAT[BT[bit]][i]
            self.DAT+=[byte]
        self.packindex()
    def packindex(self):
        'перестроение индекса пакетов'
        self.INDEX=[]
        for i in range(len(self.DAT)-31):
            if self.DAT[i:i+3]==[0x00,0x55,0xAA]:
                if self.isOkpacket(i):
                    self.INDEX+=[i]
    def isOkpacket(self,addr):
        CH,CL=self.DAT[addr+30:addr+30+2]
        return self.checksum(addr) == CH*0x100+CL
    def checksum(self,addr):
        'вычисление контрольной суммы пакета начинающегося с адреса addr'
        return sum(self.DAT[addr:addr+29+1])
    def __str__(self):
        T='Поток %s: %s'%(self.ID,self.BT)
#         T+=dump(self.DAT)
        return T
    def packages(self): return self.INDEX
    def package(self,addr): return self.DAT[addr:addr+32]

print
K1=ByteStream('K1',CHBT['K1']) ; print K1
K2=ByteStream('K2',CHBT['K2']) ; print K2
K3=ByteStream('K3',CHBT['K3']) ; print K3

############# вспомогательные функции ###############

def BF(dat,base,bitdef):
    'разбор битовых полей'
    N=0
    for i in bitdef:
        BYTE,BITS=i ; BYTE-=base
        for b in range(BITS[0],BITS[1]+1):
            N=(N<<1)|(dat[BYTE]>>(8-b))&1
    return N

def HD(dat):
    'hexdump списка'
    return '[%s]'%(\
        reduce(lambda a,b:'%s %s'%(a,b),\
               map(lambda x:'%.2X'%x,dat)))

############# классы полей кадра ###############

class vDumpable:
    def dump(self): return HD(self.DAT)

class Signatura(vDumpable):
    'Заголовок'
    def __init__(self,dat):
        assert len(dat)==3
        self.DAT=dat
    def __str__(self): return self.dump()
class AnyTime(vDumpable):
    'метка времени'
    def __init__(self,dat):
        assert len(dat)==4
        self.DAT=dat
        self.SEC= BF(dat,4,[(4,(0,5))])
        self.MIN= BF(dat,4,[(4,(6,7)),(5,(0,3))])
        self.HOUR=BF(dat,4,[(5,(4,7)),(6,(0,0))])
        self.DAYS=BF(dat,4,[(6,(1,7)),(7,(0,7))])
    def __str__(self): return '%.2i:%.2i:%.2i:%.2i'%(\
            self.DAYS,self.HOUR,self.MIN,self.SEC)
class ShtyrTime(AnyTime):
    'Время Штиля'
class BSKVU(AnyTime):
    'Фремя БСКВУ'
class PeakDM(vDumpable):
    'пик ДМ'
    def __init__(self,dat):
        assert len(dat)==5
        self.DAT=dat
        self.X =BF(dat,16,[(16,(0,7)),(17,(0,3))])
        self.Y =BF(dat,16,[(17,(4,7)),(18,(0,7))])
        self.Z =BF(dat,16,[(19,(0,7)),(20,(0,7))])
    def __str__(self): 
        return 'X:%i Y:%i Z:%i'%(\
            self.X,self.Y,self.Z)
    def module(self):
        return math.sqrt(self.X**2+self.Y**2+self.Z**2) 
    def html(self): 
        return '<td>%s</td><td>%s</td><td>%s</td>'%(\
            self.X,self.Y,self.Z)
class Termo(vDumpable):
    'Температура'
    def __init__(self,dat):
        assert len(dat)==4
        self.DAT=dat
        self.DM1 =BF(dat,26,[(26,(0,7)),(27,(0,3))])
        self.DM2 =BF(dat,26,[(27,(4,7)),(28,(0,7))])
        self.SHT =BF(dat,26,[(29,(0,7))])
    def __str__(self): return '%s\tDM1:%i DM2:%i SHT:%i'%(HD(self.DAT),\
            self.DM1,self.DM2,self.SHT)
    def html(self): return '<td>%s</td><td>%s</td><td>%s</td>'%(\
            self.DM1,self.DM2,self.SHT)

############# класс кадра ###############

class Frame1:
    'пакет'
    def __init__(self,ch,addr,block):
        assert len(block)==32
        self.CH=ch
        self.ADDR=addr
        self.DAT=block
        # декодирование с выделением срезов из списка байт
        self.type       =self.DAT[0]+1
        self.signature  =Signatura( self.DAT[0:2+1] )
        self.blockN     =           self.DAT[3]
        self.time       =ShtyrTime( self.DAT[4:7+1])
        self.BSKVU1     =BSKVU(     self.DAT[8:11+1])
        self.BSKVU2     =BSKVU(     self.DAT[12:15+1])
        self.DM1peak    =PeakDM(    self.DAT[16:20+1])
        self.DM2peak    =PeakDM(    self.DAT[21:25+1])
        self.Temp       =Termo(     self.DAT[26:29+1])
        self.CRC_H      =           self.DAT[30]
        self.CRC_L      =           self.DAT[31]
    def checksum(self,addr): return sum(self.DAT[0,29+1])
    def __str__(self):
        HL='-'*55
        T='Пакет %.2X %s@%.4X\n'%(self.type,self.CH,self.ADDR)+HL
        T+=dump(self.DAT)
        T+='\n'+HL
        T+='\nсигнатура:\t\t%s'%self.signature
        T+='\n№ блока:\t\t%.2X'%self.blockN
        T+='\nвремя Штыря:\t%s\t\t%s'%(self.time.dump(),self.time)
        T+='\nБСКВУ1:\t\t\t%s\t\t%s'%(self.BSKVU1.dump(),self.BSKVU1)
        T+='\nБСКВУ2:\t\t\t%s\t\t%s'%(self.BSKVU2.dump(),self.BSKVU2)
        T+='\nПик DM1:\t\t%s\t%s'%(self.DM1peak.dump(),self.DM1peak)
        T+='\nПик DM2:\t\t%s\t%s'%(self.DM2peak.dump(),self.DM2peak)
        T+='\nТемпература:\t%s'%self.Temp
        T+='\nCRC_H:\t\t\t%.2X'%self.CRC_H
        T+='\nCLC_L:\t\t\t%.2X'%self.CRC_L
        T+='\n'+HL
        return T
    HTMLHEADER='''
<H1>Кадр 1</H1>
<table cellpadding=5 border=1>
<tr>
<td rowspan=3>Номер<br>блока</td>
<td rowspan=3>Время<br>Штиль</td>
<td rowspan=3>Время<br>БСКВУ1</td>
<td rowspan=3>Время<br>БСКВУ2</td>
<td colspan=6>Магнитное поле в наноПопугаях</td>
<td colspan=3 rowspan=2>Температура</td>
</tr>
<tr>
<td colspan=3>DM1</td>
<td colspan=3>DM2</td>
</tr>
<tr>
<td>X</td>
<td>Y</td>
<td>Z</td>
<td>X</td>
<td>Y</td>
<td>Z</td>
<td>DM1</td>
<td>DM2</td>
<td>Штиль</td>
</tr>
'''
    def html(self):
        return '''<tr><td>%i</td><td>%s</td><td>%s</td><td>%s</td>%s%s%s</tr>'''%(\
            self.blockN,\
            self.time,self.BSKVU1,self.BSKVU2,\
            self.DM1peak.html(),self.DM2peak.html(),
            self.Temp.html()
            )

BLKSET={}
for K in [K1,K2,K3]:
    for P in K.packages():
        F=Frame1(K.ID,P,K.package(P))
        print
        print F
        BLKSET[F.blockN]=F
print >>HTML1,Frame1.HTMLHEADER
for B in sorted(BLKSET.keys()):
    print >>HTML1,BLKSET[B].html()
print >>HTML1,'''
</table>
'''

print >>HTML1,'''
</html>
'''
