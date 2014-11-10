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

class HTML:
    def __init__(self, FileName, Title):
        self.FileName = FileName
        self.Title = Title
        self.SubTitle = ''
        self.dat = ''
    def __del__(self): 
        self.fh = open(self.FileName, 'w')
        print >> self.fh, '<html>\n<title>%s</title>\n<body>\n<h1>%s</h1>' % (self.Title, self.SubTitle)
        print >> self.fh, self.dat
        print >> self.fh, '</body>\n</html>\n'
        self.fh.close()
    def write(self, S): self.dat += S
    def __setitem__(self,tag,val):
        if tag=='td':
            self.write('<td>%s</td>'%str(val))
        else:
            self.write('<pre>%s</pre>'%str(val))

# выходные файлы с отчетами, открывать в Excel или браузере
# HTML1 = open('%s/kadr1.html'%DATDIR,'w')
# HTML2 = open('%s/kadr2.html'%DATDIR,'w')
# HTML3 = open('%s/kadr3.html'%DATDIR,'w')
# HTML4 = open('%s/kadr4.html'%DATDIR,'w')
# HTMLS = open('%s/stat.html'%DATDIR,'w')
K1LOG = HTML('%s/K1.html'%DATDIR,'Канал 1 (row): %s'%DATDIR)
K2LOG = HTML('%s/K2.html'%DATDIR,'Канал 2 (row): %s'%DATDIR)
K3LOG = HTML('%s/K3.html'%DATDIR,'Канал 3 (row): %s'%DATDIR)
KADR12 = HTML('%s/kadr12.html'%DATDIR,'Кадры 1/2: %s'%DATDIR)

P1LOG = HTML('%s/P1.html'%DATDIR,'Пакет 1: %s'%DATDIR)
print >>P1LOG,'''
<table border=1 cellpadding=3>
<tr bgcolor="lightblue">
<td rowspan=2>канал</td>
<td rowspan=2>№ пакета</td>
<td rowspan=2>адрес</td>
<td colspan=3>Время</td>
<td colspan=3>Пиковое DM1</td>
<td colspan=3>Пиковое DM2</td>
<td colspan=3>Температура</td>
</tr>
<tr bgcolor="lightcyan">
<td>Штиля</td>
<td>БСКВУ1</td>
<td>БСКВУ2</td>
<td>X</td><td>Y</td><td>Z</td>
<td>X</td><td>Y</td><td>Z</td>
<td>DM1</td>
<td>DM2</td>
<td>Штиль</td>
</tr>
'''

P2LOG = HTML('%s/P2.html'%DATDIR,'Пакет 2: %s'%DATDIR)
print >>P2LOG,'''
<table border=1 cellpadding=3>
<tr bgcolor="lightblue">
<td rowspan=2>канал</td>
<td rowspan=2>№ пакета</td>
<td rowspan=2>адрес</td>
<td colspan=3>U питания</td>
<td colspan=3>DM1</td>
<td colspan=3>DM2</td>
<td colspan=6>Напряжение шина-корпус</td>
</tr>
<tr bgcolor="lightcyan">
<td>min</td>
<td>max</td>
<td>сред</td>
<td>X</td><td>Y</td><td>Z</td>
<td>X</td><td>Y</td><td>Z</td>
<td>U1</td>
<td>U2</td>
<td>U3</td>
<td>U4</td>
<td>U5</td>
<td>U6</td>
</tr>
'''

######################################################

import os,time,re,math

# выходной файл лога
# sys.stdout=open('log.log','w')

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

def bgcolor(F):
    return {True:"lightgreen", False:"yellow"}[F]

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
    def __init__(self, DAT): self.DAT = DAT
    def __str__(self): return HD(self.DAT)

class AnyTime:
    'метка времени'
    def __init__(self, DAT):
        assert len(DAT) == 4
        self.DAT = DAT ; D = DAT ; D.reverse()
        N = reduce(lambda a, b:a << 8 | b, D)
        self.SEC = N & 0b111111 ; N = N >> 6
        self.MIN = N & 0b111111 ; N = N >> 6
        self.HOUR = N & 0b11111  ; N = N >> 5
        self.DAYS = N
    def __str__(self): return '%s' % self.ts()
    def ts(self): return '%.2i:%.2i:%.2i:%.2i'%(self.DAYS, self.HOUR, self.MIN, self.SEC )

class ShtyrTime(AnyTime):
    'Время Штиля'
class BSKVU(AnyTime):
    'Фремя БСКВУ'

class MagnetField:
    'магнитное поле'
    def __init__(self, DAT):
        assert len(DAT) == 5
        self.DAT = DAT ; D = DAT ; D.reverse()
        N = reduce(lambda a, b:a << 8 | b, D)
        self.X = N & 0b111111111111 ; N = N >> 12
        self.Y = N & 0b111111111111 ; N = N >> 12
        self.Z = N & 0b111111111111
    def __str__(self): 
        return 'X:%i Y:%i Z:%i' % (\
            self.X, self.Y, self.Z)
#     def module(self):
#         return math.sqrt(self.X**2+self.Y**2+self.Z**2) 
#     def html(self): 
#         return '<td>%s</td><td>%s</td><td>%s</td>'%(\
#             self.X,self.Y,self.Z)

class Termo:
    'Температура'
    def __init__(self, DAT):
        assert len(DAT) == 4
        self.DAT = DAT ; D = DAT ; D.reverse()
        N = reduce(lambda a, b:a << 8 | b, D)
        self.DM1 = N & 0b111111111111 ; N = N >> 12
        self.DM2 = N & 0b111111111111 ; N = N >> 12
        self.SHT = N & 0b11111111
    def __str__(self): 
        return '%s\tDM1:%i DM2:%i SHT:%i' % (HD(self.DAT), \
            self.DM1, self.DM2, self.SHT)
#     def html(self): return '<td>%s</td><td>%s</td><td>%s</td>'%(\
#             self.DM1,self.DM2,self.SHT)

class Upit:
    'Напряжения питания'
    def __init__(self, DAT):
        assert len(DAT) == 4
        self.DAT = DAT ; D = DAT ; D.reverse()
        N = reduce(lambda a, b:a << 8 | b, D)
        self.MIN = N & 0b1111111111 ; N = N >> 10
        self.MAX = N & 0b1111111111 ; N = N >> 10
        self.MED = N & 0b1111111111
    def __str__(self): 
        return '%s %s %s %s' % (
            self.MIN, self.MAX, self.MED, HD(self.DAT))
#     def html(self): return '<td>%.2f</td><td>%.2f</td><td>%.2f</td>'%(\
#         self.MIN,self.MED,self.MAX)

class Shina:
    'Шина-Корпус'
    def __init__(self, N, DAT):
        assert len(DAT) == 29 - 18 + 1
        self.N = N
        self.DAT = DAT ; D = DAT ; D.reverse()
        N = reduce(lambda a, b:a << 8 | b, D)
        self.SK1 = N & 0b1111111111 ; N = N >> 16
        self.SK2 = N & 0b1111111111 ; N = N >> 16
        self.SK3 = N & 0b1111111111 ; N = N >> 16
        self.SK4 = N & 0b1111111111 ; N = N >> 16
        self.SK5 = N & 0b1111111111 ; N = N >> 16
        self.SK6 = N & 0b1111111111
    def __str__(self): 
        return '%s %s %s %s %s %s %s' % (
            self.SK1, self.SK2, self.SK3,
            self.SK4, self.SK5, self.SK6,
            HD(self.DAT))

############################
# классы пакетов
############################

class Package:
    'пакет общий код'
    def __init__(self, CH, ADDR, DAT):
        self.CH = CH
        self.ADDR = ADDR
        self.DAT = DAT
        # декодирование с выделением срезов из списка байт
        self.SIGN = Signatura(self.DAT[0:3])
        self.N = self.DAT[3]
        try:
            self.Type = {0:1, 1:2, 2:3, 255:4}[self.DAT[0]]
        except KeyError:
            self.Type = self.DAT[0]
        self.N = self.DAT[3]
        self.CRC_H = self.DAT[30]
        self.CRC_L = self.DAT[31]
        self.OK = self.isValid()
    def __str__(self):
        T = '\n<a name="%s">Пакет %s@%s\n' % (self.ADDR, self.ADDR, self.CH)
        T += '-' * 40 + dump(self.DAT) + '-' * 40 + '\n'
        T += 'сигнатура: %s\n' % self.SIGN
        T += '# блока: %s\n' % self.N
        T += 'тип: %s\n' % self.Type
        T += 'CRC_H: %s\n' % self.CRC_H
        T += 'CRC_L: %s\n' % self.CRC_L
        T += 'валидность: %s\n' % self.OK
        T += '-' * 40 + '\n'
        return T
    def html(self):
        T = '<tr bgcolor="%s">' % bgcolor(self.OK)
        T += '<td><a href="#%s">#%s</a></td>' % (self.ADDR, self.ADDR)
        T += reduce(lambda a, b:a + b, map(lambda x:'<td>%s</td>' % x, self.DAT))
        T += '</tr>\n'
        return T
    def isValid(self): return self.CRC() == (self.CRC_H << 8) | self.CRC_L
    def CRC(self): return sum(self.DAT[:-2])
    
class Report:
    def __init__(self): 
        self.dat={}
#     def __getitem__(self,idx):
#         try:
#             return self.dat[idx]
#         except KeyError:
#             self.dat[idx]={}
#             return self.dat[idx]
#     def put(self,CH,N,FLD,VAL):
#         self.dat+=[(CH,N,FLD,VAL)]
#     def htd(self,IDX,FLD,VAL):
#         try:
#             T=self.dat[IDX][FLD]
#         except KeyError:
#             T='???[%s]%s???'%(IDX,FLD)
#         bgc=bgcolor(self.dat[IDX][VAL])
#         return '<td bgcolor="%s">%s</td>'%(bgc,T)
    
class Report12(Report):
    'Отчет по пакетам 1/2'
    def __str__(self): return 'Отчет по кадрам 1/2'
    def html(self):
        T=self.HTMLTABLEHEAD
# #         for i in self.dat:
# #             T+='<tr><td>%s</td></tr>\n'%str(i)
#         T+='</table>\n'
#         for i in self.dat:
#             T+='<pre>%s\n%s</pre>\n'%(str(i),str(self.dat[i]))
        return T
    HTMLTABLEHEAD='''
<table border=1 cellpadding=3>
<tr bgcolor="lightblue">
<td rowspan=2>#</td>
<td colspan=3>Время</td>
<td colspan=6>Максимальное значение<br>магнитного поля<br>в микроПопугаях</td>
<td colspan=6>Текущее значение<br>магнитного поля<br>в микроПопугаях</td>
<td colspan=3>Напряжение питания<br>мегаБолт</td>
<td colspan=6>Напряжение шина-корпус<br>мегаБолт</td>
</tr>
<tr bgcolor="lightcyan">
<td>Штыря</td>
<td>БСКВУ1</td>
<td>БСКВУ2</td>
<td>X1</td><td>Y1</td><td>Z1</td>
<td>X2</td><td>Y2</td><td>Z2</td>
<td>X1</td><td>Y1</td><td>Z1</td>
<td>X2</td><td>Y2</td><td>Z2</td>
<td>min</td><td>max</td><td>среднее</td>
<td>U1</td><td>U2</td><td>U3</td>
<td>U3</td><td>U4</td><td>U5</td>
</tr>
'''
R12 = Report12()     
    
class Package1(Package):
    'пакет тип кадр1'
    def __init__(self, CH, ADDR, DAT):
        # вызов конструктора суперкласса
        Package.__init__(self, CH, ADDR, DAT)
        # декодирование полей специфичных для кадра1
        self.time = ShtyrTime(self.DAT[4:7 + 1])
        self.BSKVU1 = BSKVU(self.DAT[8:11 + 1])
        self.BSKVU2 = BSKVU(self.DAT[12:15 + 1])
        self.DM1peak = MagnetField(self.DAT[16:20 + 1])
        self.DM2peak = MagnetField(self.DAT[21:25 + 1])
        self.Temp = Termo(self.DAT[26:29 + 1])
        self.htmlreport()
    def htmlreport(self):
        # html
        print >>P1LOG,'<tr bgcolor="%s">'%bgcolor(self.OK)
        P1LOG['td']=self.CH
        P1LOG['td']=self.N
        print >>P1LOG,'<td><a href="%s.html#%s">#%s</a></td>'%(self.CH,self.ADDR,self.ADDR)
        P1LOG['td']=self.time
        P1LOG['td']=self.BSKVU1
        P1LOG['td']=self.BSKVU1
        P1LOG['td']=self.DM1peak.X
        P1LOG['td']=self.DM1peak.Y
        P1LOG['td']=self.DM1peak.Z
        P1LOG['td']=self.DM2peak.X
        P1LOG['td']=self.DM2peak.Y
        P1LOG['td']=self.DM2peak.Z
        P1LOG['td']=self.Temp.DM1
        P1LOG['td']=self.Temp.DM2
        P1LOG['td']=self.Temp.SHT
        print >>P1LOG,'</tr>'
    def __str__(self):
        # вызов дампера суперкласса
        T = Package.__str__(self)
        T += 'время Штыря: %s\n' % self.time
        T += 'время БСКВУ1: %s\n' % self.BSKVU1
        T += 'время БСКВУ2: %s\n' % self.BSKVU2
        T += 'Пик DM1: %s\n' % self.DM1peak
        T += 'Пик DM2: %s\n' % self.DM2peak
        T += 'Температура: %s\n' % self.Temp
        T += '-' * 40 + '\n'
        return T

class Package2(Package):
    'пакет тип кадр2'
    def __init__(self, CH, ADDR, DAT):
        # вызов конструктора суперкласса
        Package.__init__(self, CH, ADDR, DAT)
        # декодирование полей специфичных для кадра2
        self.Upit = Upit(self.DAT[4:7 + 1])
        self.DM1 = MagnetField(self.DAT[8:12 + 1]) 
        self.DM2 = MagnetField(self.DAT[13:17 + 1])
        self.SHINA = Shina(self.N, self.DAT[18:29 + 1]) 
        # html
        self.htmlreport()
    def htmlreport(self):
        print >>P2LOG,'<tr bgcolor="%s">'%bgcolor(self.OK)
        P2LOG['td']=self.CH
        P2LOG['td']=self.N
        print >>P2LOG,'<td><a href="%s.html#%s">#%s</a></td>'%(self.CH,self.ADDR,self.ADDR)
        P2LOG['td']=self.Upit.MIN
        P2LOG['td']=self.Upit.MAX
        P2LOG['td']=self.Upit.MED
        P2LOG['td']=self.DM1.X
        P2LOG['td']=self.DM1.Y
        P2LOG['td']=self.DM1.Z
        P2LOG['td']=self.DM2.X
        P2LOG['td']=self.DM2.Y
        P2LOG['td']=self.DM2.Z
        P2LOG['td']=self.SHINA.SK1
        P2LOG['td']=self.SHINA.SK2
        P2LOG['td']=self.SHINA.SK3
        P2LOG['td']=self.SHINA.SK4
        P2LOG['td']=self.SHINA.SK5
        P2LOG['td']=self.SHINA.SK6
        print >>P2LOG,'</tr>'
    def __str__(self):
        # вызов дампера суперкласса
        T = Package.__str__(self)
        T += 'U питания: %s\n' % self.Upit
        T += 'DM1: %s\n' % self.DM1
        T += 'DM2: %s\n' % self.DM2
        T += 'Шина-Корпус: %s\n' % self.SHINA
        T += '-' * 40 + '\n'
        return T

class Channel:
    'канал: поток байтовых данных'
    def __init__(self, ID, BT):
        self.ID = ID
        self.BT = BT
        self.DAT = []
        self.SZ = len(DAT[(1, 1)])
        for i in range(self.SZ):
            byte = 0
            for bit in range(8):
                byte = byte * 2 + DAT[BT[bit]][i]
            self.DAT += [byte]
        self.packindex()
        self.PACKS = []
        for a in self.INDEX:
            T = self.package(a)
            if T[0] == 0: P = Package1(self.ID, a, T)
            elif T[0] == 1: P = Package2(self.ID, a, T)
            else: P = Package(self.ID, a, T)
            self.PACKS.append(P)
    def packindex(self):
        'перестроение индекса пакетов'
        self.INDEX = []
        for i in range(len(self.DAT) - 31):
            if self.DAT[i + 1:i + 3] == [0x55, 0xAA]:
                self.INDEX += [i]
    def __str__(self):
        return 'Канал %s [%i байт, %i пакетов]' % (self.ID, self.SZ, len(self.INDEX))
    def html(self):
        T = '<table border=1 cellpadding=3>\n'
        for P in self.PACKS: T += P.html()
        T += '</table>\n'
        for P in self.PACKS: T += '<pre>%s</pre>\n' % P
        return T
    def packages(self): return self.PACKS
    def package(self, addr): return self.DAT[addr:addr + 32]
    def __iter__(self): return iter(self.INDEX)

print
K1 = Channel('K1', BitMap['K1']) ; print K1 ; K1LOG.SubTitle = K1 ; print >> K1LOG, K1.html()
K2 = Channel('K2', BitMap['K2']) ; print K2 ; K2LOG.SubTitle = K1 ; print >> K2LOG, K2.html()
K3 = Channel('K3', BitMap['K3']) ; print K3 ; K3LOG.SubTitle = K1 ; print >> K3LOG, K3.html()

print R12 ; KADR12.SubTitle = R12 ; print >> KADR12, R12.html()

print >>P1LOG,'</table>'

print '.'
