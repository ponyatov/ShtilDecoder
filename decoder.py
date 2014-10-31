# -*- coding: cp1251 -*-
# Декодер файлов Штыря №2
# нужен 
# интерпретатор Python 2.7.x:
#     https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi
# GnuPlot:
#     http://sourceforge.net/projects/gnuplot/files/gnuplot/4.6.6/gp466-win32-setup.exe/download
######################################################

import sys

# каталог с данными
try:
    DATDIR = sys.argv[1]
except IndexError:
    DATDIR='dat/3' 
    DATDIR = r'\\arhive\Public\Arseniy\Штиль-М\06 прот'
    DATDIR = r'\\arhive\Public\Arseniy\Shtil Decoder\3'

# маска имени файла
DATFILEMASK = '%s/374ШИМП_%i (%i)(K).dat'

# расположение бинарника GnuGlot
GNUPLOT = r'gnuplot\gnuplot.exe' 

BitMap={
# разбитовка каналов: байт 76543210
#        0      1      2      3      4      5      6      7
'K1':[(1,8 ),(1,7 ),(1,6 ),(1,5 ),(1,4 ),(1,3 ),(1,2 ),(1,1 )],
'K2':[(2,4 ),(2,3 ),(2,2 ),(2,1 ),(1,12),(1,11),(1,10),(1,9 )],
'K3':[(2,12),(2,11),(2,10),(2,9 ),(2,8 ),(2,7 ),(2,6 ),(2,5 )]
}

# выходные файлы с отчетами, открывать в Excel или браузере
HTML1 = open('%s/kadr1.html'%DATDIR,'w')
HTML2 = open('%s/kadr2.html'%DATDIR,'w')
HTML3 = open('%s/kadr3.html'%DATDIR,'w')
HTML4 = open('%s/kadr4.html'%DATDIR,'w')
HTMLS = open('%s/stat.html'%DATDIR,'w')
K1LOG = open('%s/K1.html'%DATDIR,'w')
K2LOG = open('%s/K2.html'%DATDIR,'w')
K3LOG = open('%s/K3.html'%DATDIR,'w')

######################################################

import os,time,re,math

# выходной файл лога
# sys.stdout=open('log.log','w')

print >>HTML1,'<html><title>Кадр 1: %s</title>'%DATDIR
print >>HTML2,'<html><title>Кадр 2: %s</title>'%DATDIR
print >>HTML3,'<html><title>Кадр 3: %s</title>'%DATDIR
print >>HTML4,'<html><title>Кадр 4: %s</title>'%DATDIR
print >>HTMLS,'<html><title>Статистика: %s</title>'%DATDIR
print >>K1LOG,'<html>'
print >>K2LOG,'<html>'
print >>K3LOG,'<html>'

print time.localtime()[:6],sys.argv
print '\nDATDIR "%s"\n'%DATDIR
print 'DATFILEMASK "%s"\n'%DATFILEMASK

def dump(dat):
    'функция вывода кекс-дампа'
    T=''
    for addr in range(len(dat)):
        if addr%0x10==0: T+='\n%.4X: '%addr
        T+='%.2X '%dat[addr]
    T+='\n'
    return T

############################
# класс статистики
############################

class Statistics:
    'статистика по битым пакетам'
STAT=Statistics()

#     def __init__(self): self.dat={}
#     def __getitem__(self,item):
#         try:
#             T = self.dat[item]
#         except KeyError:
#             T = 0 
#         return T
#     def __setitem__(self,item,value):
#         self.dat[item]=value
#     def __str__(self):
#         T='<table border=1 cellpadding=3>\n'
#         T+='<tr bgcolor=lightcyan>'
#         T+='<td>тип</td>'
#         T+='<td>всего</td>'
#         T+='<td colspan=2>битых</td>'
#         T+='<td>распознавание</td>'
#         T+='</tr>\n'
#         X={}
#         for i in self.dat:
#             X[i[0]]=0
#         del X['c']
#         T+=self.htline('c')
#         for i in sorted(X): T+=self.htline(i)
#         T+='</table>\n'
#         return T
#     def htline(self,i):
#         if i=='c':
#             x='всего'
#             T='<tr bgcolor="#FFFFAA">'
#         else:
#             x=i
#             if x==256: x=3
#             T='<tr>'
#         obs=self.dat[i,'obs']
#         bit=self.dat[i,'bit']
#         proc=100*float(bit)/obs
#         T+='<td><a href="kadr%s.html">%s</a></td>'%(x,x)
#         T+='<td>%s</td>'%obs
#         T+='<td>%s</td><td>%.1f%%</td><td>%.1f%%</td>'%(bit,proc,100-proc/2)
#         T+='</tr>\n'
#         if proc>95:
#             return ''
#         else:
#             return T

############################
# классы низкоуровневых данных
# полученных с испытательного стенда
############################

class BitStream:
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
        return 'БитПоток %i:%i\t%s\t[%i]'%(\
            self.i,self.j,\
            self.DatFileName,\
            len(self))
    def __len__(self): return len(self.dat)
    def __getitem__(self,idx): return self.dat[idx]

# загрузка каналов из файлов

DAT={}
for i in [1,2]:
    for j in range(1,12+1):
        DAT[(i,j)]=BitStream(i,j)
        print DAT[(i,j)]

############################
# вспомогательные функции
############################

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

############################
# классы полей данных
############################

class Signatura:
    'Заголовок'
    def __init__(self,DAT): self.DAT=DAT
    def __str__(self): return HD(self.DAT)

class AnyTime:
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

class MagnetField:
    'магнитное поле'
    def __init__(self,dat):
        assert len(dat)==5
        self.DAT=dat
        self.X =BF(dat,16,[(16,(0,7)),(17,(0,3))])
        self.Y =BF(dat,16,[(17,(4,7)),(18,(0,7))])
        self.Z =BF(dat,16,[(19,(0,7)),(20,(0,7))])
    def __str__(self): 
        return 'X:%i Y:%i Z:%i'%(\
            self.X,self.Y,self.Z)
#     def module(self):
#         return math.sqrt(self.X**2+self.Y**2+self.Z**2) 
#     def html(self): 
#         return '<td>%s</td><td>%s</td><td>%s</td>'%(\
#             self.X,self.Y,self.Z)

class Termo:
    'Температура'
    def __init__(self,dat):
        assert len(dat)==4
        self.DAT=dat
        self.DM1 =BF(dat,26,[(26,(0,7)),(27,(0,3))])
        self.DM2 =BF(dat,26,[(27,(4,7)),(28,(0,7))])
        self.SHT =BF(dat,26,[(29,(0,7))])
    def __str__(self): 
        return '%s\tDM1:%i DM2:%i SHT:%i'%(HD(self.DAT),\
            self.DM1,self.DM2,self.SHT)
#     def html(self): return '<td>%s</td><td>%s</td><td>%s</td>'%(\
#             self.DM1,self.DM2,self.SHT)

class Upit:
    'Напряжения питания'
    def __init__(self,DAT):
        assert len(DAT)==4
        self.DAT=DAT
    def __str__(self): return HD(self.DAT)
#         self.MIN=0.0
#         self.MED=0.0
#         self.MAX=0.0
#     def html(self): return '<td>%.2f</td><td>%.2f</td><td>%.2f</td>'%(\
#         self.MIN,self.MED,self.MAX)

class Shina:
    'Шина-Корпус'
    def __init__(self,N,DAT):
        assert len(DAT)==29-18+1
        self.N = N
        self.DAT = DAT
    def __str__(self): return HD(self.DAT)
#         self.SK1=BF(dat,18,[(18,(0,7)),(19,(0,1))])
#         self.SK2=BF(dat,18,[(20,(0,7)),(21,(0,1))])
#         self.SK3=BF(dat,18,[(22,(0,7)),(23,(0,1))])
#         self.SK4=BF(dat,18,[(24,(0,7)),(25,(0,1))])
#         self.SK5=BF(dat,18,[(26,(0,7)),(27,(0,1))])
#         self.SK6=BF(dat,18,[(28,(0,7)),(29,(0,1))])
        

############################
# классы пакетов
############################

class Package:
    'пакет общий код'
    def __init__(self,CH,ADDR,DAT):
        self.CH = CH
        self.ADDR = ADDR
        self.DAT = DAT
        # декодирование с выделением срезов из списка байт
        self.SIGN = Signatura( self.DAT[0:3] )
        self.N = self.DAT[3]
        try:
            self.Type = {0:1,1:2,2:3,255:4}[self.DAT[0]]
        except KeyError:
            self.Type = self.DAT[0]
        self.N = self.DAT[3]
        self.CRC_H = self.DAT[30]
        self.CRC_L = self.DAT[31]
        self.OK = self.isValid()
    def __str__(self):
        T='\n<a name="%s">Пакет %s@%s\n'%(self.ADDR,self.ADDR,self.CH)
        T+='-'*40+dump(self.DAT)+'-'*40+'\n'
        T+='сигнатура: %s\n'%self.SIGN
        T+='# блока: %s\n'%self.N
        T+='тип: %s\n'%self.Type
        T+='CRC_H: %s\n'%self.CRC_H
        T+='CRC_L: %s\n'%self.CRC_L
        T+='валидность: %s\n'%self.OK
        T+='-'*40+'\n'
        return T
    def html(self):
        T='<tr bgcolor="%s">'%({True:"lightgreen",False:"yellow"}[self.OK])
        T+='<td><a href="#%s">#%s</a></td>'%(self.ADDR,self.ADDR)
        T+=reduce(lambda a,b:a+b,map(lambda x:'<td>%s</td>'%x,self.DAT))
        T+='</tr>\n'
        return T
    def isValid(self): return self.CRC()==(self.CRC_H<<8)|self.CRC_L
    def CRC(self): return sum(self.DAT[:-2])
    
class Package1(Package):
    'пакет тип кадр1'
    def __init__(self,CH, ADDR, DAT):
        # вызов конструктора суперкласса
        Package.__init__(self, CH, ADDR, DAT)
        # декодирование полей специфичных для кадра1
        self.time    =ShtyrTime(  self.DAT[4:7+1])
        self.BSKVU1  =BSKVU(      self.DAT[8:11+1])
        self.BSKVU2  =BSKVU(      self.DAT[12:15+1])
        self.DM1peak =MagnetField(self.DAT[16:20+1])
        self.DM2peak =MagnetField(self.DAT[21:25+1])
        self.Temp    =Termo(      self.DAT[26:29+1])
    def __str__(self):
        # вызов дампера суперкласса
        T=Package.__str__(self)
        T+='время Штыря: %s\n'%self.time
        T+='время БСКВУ1: %s\n'%self.BSKVU1
        T+='время БСКВУ2: %s\n'%self.BSKVU2
        T+='Пик DM1: %s\n'%self.DM1peak
        T+='Пик DM2: %s\n'%self.DM2peak
        T+='Температура: %s\n'%self.Temp
        T+='-'*40+'\n'
        return T

class Package2(Package):
    'пакет тип кадр2'
    def __init__(self,CH, ADDR, DAT):
        # вызов конструктора суперкласса
        Package.__init__(self, CH, ADDR, DAT)
        # декодирование полей специфичных для кадра2
        self.Upit  = Upit(self.DAT[4:7+1])
        self.DM1   = MagnetField(self.DAT[8:12+1]) 
        self.DM2   = MagnetField(self.DAT[13:17+1])
        self.SHINA = Shina(self.N,self.DAT[18:29+1]) 
    def __str__(self):
        # вызов дампера суперкласса
        T=Package.__str__(self)
        T+='U питания: %s\n'%self.Upit
        T+='DM1: %s\n'%self.DM1
        T+='DM2: %s\n'%self.DM2
        T+='Шина-Корпус: %s\n'%self.SHINA
        T+='-'*40+'\n'
        return T

class Channel:
    'канал: поток байтовых данных'
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
        self.PACKS=[]
        for a in self.INDEX:
            T=self.package(a)
            if T[0]==0: P=Package1(self.ID,a,T)
            elif T[0]==1: P=Package2(self.ID,a,T)
            else: P=Package(self.ID,a,T)
            self.PACKS.append(P)
    def packindex(self):
        'перестроение индекса пакетов'
        self.INDEX=[]
        for i in range(len(self.DAT)-31):
            if self.DAT[i+1:i+3]==[0x55,0xAA]:
                self.INDEX+=[i]
    def __str__(self):
        return 'Канал %s [%i байт, %i пакетов]'%(self.ID,self.SZ,len(self.INDEX))
    def html(self):
        T='<title>%s</title><H1>%s</H1>\n'%(self,self)
        T+='<table border=1 cellpadding=3>\n'
        for P in self.PACKS: T+=P.html()
        T+='</table>\n'
        for P in self.PACKS: T+='<pre>%s</pre>'%P
        return T
    def packages(self): return self.PACKS
    def package(self,addr): return self.DAT[addr:addr+32]
    def __iter__(self): return iter(self.INDEX)

print
K1=Channel('K1',BitMap['K1']) ; print K1 ; print >>K1LOG,K1.html()
K2=Channel('K2',BitMap['K2']) ; print K2 ; print >>K2LOG,K2.html()
K3=Channel('K3',BitMap['K3']) ; print K3 ; print >>K3LOG,K3.html()

# print >>K1LOG,'<table border=1 cellpadding=2>'
# for P in K1.packages():
#     print >>K1LOG,Package(K1.package(P)).html()
# print >>K1LOG,'</table>'
 
print '.'

# ############# классы полей кадра ###############
# 
#     def html(self):
#         TNS='shina_%s'%self.blockN
#         TN='%s/%s'%(DATDIR,TNS)
#         T=open(TN,'w')
#         print >>T,"""
# set terminal png size 128,64
# set output '%s/%s.png'
# unset xtics
# unset ytics
# unset key
# unset border
# set bmargin 0
# set yrange [0:500]
# plot '-' w l lt -1 lw 2 """%(DATDIR,TNS)
#         D=[self.SK1,self.SK2,self.SK3,self.SK4,self.SK5,self.SK6]
#         for i in range(len(D)):
#             print >>T,'%s\t%s'%(i,D[i])
#         print >>T,''
#         T.close()
#         CMD=r'%s "%s"'%(GNUPLOT,TN) ; print CMD
# #         os.system(CMD) 
#         os.remove(TN)
#         return '<td><img src="%s.png" alt="%s %s %s %s %s %s"></td>'%(\
#         TNS,\
#         self.SK1,self.SK2,self.SK3,self.SK4,self.SK5,self.SK6)
# 
# ############# класс кадра ###############
# 
# class Frame:
#     def __init__(self,ch,addr,block):
#         # накопление статистики
#         STATBROK[('c','obs')] += 1
#         STATBROK[(self.type,'obs')] += 1
#         if not self.Valid: 
#             STATBROK[('c','bit')] +=1
#             STATBROK[(self.type,'bit')] +=1
#     HTMLFOOTER='</table>'
#     HEADBGCOLOR='#DDDDFF'
# 
# class Frame4(Frame):
#     'пакет тип кадр4'
#     def html(self): return '<tr><td>%s</td><td></td><td></td><td></td></tr>'%self.blockN
#     HTMLHEADER='''
# <H1>Кадр 4</H1>
# <table cellpadding=5 border=1>
# <tr bgcolor='''+Frame.HEADBGCOLOR+'''>
# <td>Номер<br>блока</td>
# <td>Время</td>
# <td>Источник<br>сообщения</td>
# <td>№ подблока</td>
# <td>Отсчеты АЦП</td>
# </tr>
# '''
# 
# class Frame3(Frame):
#     'пакет тип кадр3'
#     def html(self): return '<tr><td>%s</td><td></td><td></td><td></td></tr>'%self.blockN
#     HTMLHEADER='''
# <H1>Кадр 3</H1>
# <table cellpadding=5 border=1>
# <tr bgcolor='''+Frame.HEADBGCOLOR+'''>
# <td>Номер<br>блока</td>
# <td>Время</td>
# <td>№ подблока</td>
# <td>Отсчеты АЦП</td>
# </tr>
# '''
# # <tr bgcolor=#AAFFAA>
# # <td colspan=3>DM1</td>
# # <td colspan=3>DM2</td>
# # </tr>
# # <tr bgcolor=#AAFFAA>
# # <td>min</td>
# # <td>среднее</td>
# # <td>max</td>
# # <td>X</td>
# # <td>Y</td>
# # <td>Z</td>
# # <td>X</td>
# # <td>Y</td>
# # <td>Z</td>
# # </tr>
# 
# class Frame2(Frame):
#     'пакет тип кадр2'
#     def __init__(self,ch,addr,block):
#         Frame.__init__(self, ch, addr, block)
#         # декодирование с выделением срезов из списка байт
#     def __str__(self):
#         T=Frame.__str__(self)
#         return T
#     HTMLHEADER='''
# <H1>Кадр 2</H1>
# <table cellpadding=5 border=1>
# <tr bgcolor='''+Frame.HEADBGCOLOR+'''>
# <td rowspan=3>Номер<br>блока</td>
# <td rowspan=2 colspan=3>U питания<br>в Болтах</td>
# <td colspan=6>Магнитное поле в наноПопугаях</td>
# <td rowspan=3>Шина<br>Корпус</td>
# </tr>
# <tr bgcolor=#AAFFAA>
# <td colspan=3>DM1</td>
# <td colspan=3>DM2</td>
# </tr>
# <tr bgcolor=#AAFFAA>
# <td>min</td>
# <td>среднее</td>
# <td>max</td>
# <td>X</td>
# <td>Y</td>
# <td>Z</td>
# <td>X</td>
# <td>Y</td>
# <td>Z</td>
# </tr>
# '''
#     def htmlValid(self): return {True:'',False:'bgcolor=#FFAAAA'}[self.Valid] 
#     def html(self):
#         return '''<tr %s><td><a href="#%i">%i</a></td>%s%s%s%s</tr>'''%(\
#             self.htmlValid(),\
#             self.blockN,self.blockN,\
#             self.Upit.html(),\
#             self.DM1.html(),self.DM2.html(),\
#             self.SHINA.html()\
#             )
#     
# class Frame1(Frame):
#     def checksum(self,addr): return sum(self.DAT[0,29+1])
#     def __str__(self):
#         T=Frame.__str__(self)
#         T+='\n'+self.HL
#         return T
#     HTMLHEADER='''
# <H1>Кадр 1</H1>
# <table cellpadding=5 border=1>
# <tr bgcolor='''+Frame.HEADBGCOLOR+'''>
# <td rowspan=3>Номер<br>блока</td>
# <td rowspan=2 colspan=3>Время, ДД:ЧЧ:ММ:СС</td>
# <td colspan=6>Магнитное поле в наноПопугаях</td>
# <td colspan=3 rowspan=2>Температура<br>в микроГрадусниках</td>
# </tr>
# <tr bgcolor=#AAFFAA>
# <td colspan=3>DM1</td>
# <td colspan=3>DM2</td>
# </tr>
# <tr bgcolor=#AAFFAA>
# <td>Штиль</td>
# <td>БСКВУ1</td>
# <td>БСКВУ2</td>
# <td>X</td>
# <td>Y</td>
# <td>Z</td>
# <td>X</td>
# <td>Y</td>
# <td>Z</td>
# <td>DM1</td>
# <td>DM2</td>
# <td>Штиль</td>
# </tr>
# '''
#     def html(self):
#         return '''<tr %s><td><a href="#%i">%i</a></td><td>%s</td><td>%s</td><td>%s</td>%s%s%s</tr>'''%(\
#             {True:'',False:'bgcolor=#FFAAAA'}[self.Valid],
#             self.blockN,self.blockN,\
#             self.time,self.BSKVU1,self.BSKVU2,\
#             self.DM1peak.html(),self.DM2peak.html(),
#             self.Temp.html()
#             )
# 
# ############# разбор потоков K1..K3 на пакеты ###############
# 
# BLKSET1={}
# BLKSET2={}
# BLKSET3={}
# BLKSET4={}
# for K in [K1,K2,K3]:
#     for P in K.packages():
#         PACK=K.package(P)
#         if PACK[0]+1==1:
#             F=Frame1(K.ID,P,PACK) 
#             BLKSET1[F.blockN]=F
#         elif PACK[0]+1==2:
#             F=Frame2(K.ID,P,PACK) 
#             BLKSET2[F.blockN]=F
#         elif PACK[0]+1==256 and PACK[3]==200:
#             F=Frame3(K.ID,P,PACK) 
#             BLKSET3[F.blockN]=F
#         elif PACK[0]+1==256 and PACK[3]==201:
#             F=Frame4(K.ID,P,PACK) 
#             BLKSET4[F.blockN]=F
#         else:
#             F=Frame(K.ID,P,PACK)
#         print '\n%s'%F
# 
# ############# генерация отчетов ###############
# 
# print >>HTML1,Frame1.HTMLHEADER
# print >>HTML2,Frame2.HTMLHEADER
# print >>HTML3,Frame3.HTMLHEADER
# print >>HTML4,Frame4.HTMLHEADER
# 
# for B in sorted(BLKSET1.keys()):
#     BLK=BLKSET1[B]
#     print >>HTML1,BLK.html()
# print >>HTML1,Frame1.HTMLFOOTER
# for B in sorted(BLKSET1.keys()):
#     BLK=BLKSET1[B]
#     print >>HTML1,'<a name="%s">\n<pre>\n%s\n</pre>\n</a>\n'%(BLK.blockN,BLK)
# 
# for B in sorted(BLKSET2.keys()):
#     BLK=BLKSET2[B]
#     print >>HTML2,BLK.html()
# print >>HTML2,Frame2.HTMLFOOTER
# for B in sorted(BLKSET2.keys()):
#     BLK=BLKSET2[B]
#     print >>HTML2,'<a name="%s">\n<pre>\n%s\n</pre>\n</a>\n'%(BLK.blockN,BLK)
# 
# for B in sorted(BLKSET3.keys()):
#     BLK=BLKSET3[B]
#     print >>HTML3,BLK.html()
# print >>HTML3,Frame3.HTMLFOOTER
# for B in sorted(BLKSET3.keys()):
#     BLK=BLKSET3[B]
#     print >>HTML3,'<a name="%s">\n<pre>\n%s\n</pre>\n</a>\n'%(BLK.blockN,BLK)
# 
# print >>HTML1,'</html>'
# print >>HTML2,'</html>'
# print >>HTML3,'</html>'
# print >>HTML4,'</html>'
# print >>HTMLS,'<pre>%s</pre>'%STATBROK
