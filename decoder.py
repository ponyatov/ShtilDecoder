# -*- coding: cp1251 -*-
# ������� ������ ����� �2
# ����� 
# ������������� Python 2.7.x:
#     https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi
# GnuPlot:
#     http://sourceforge.net/projects/gnuplot/files/gnuplot/4.6.6/gp466-win32-setup.exe/download
######################################################

import sys

# ������� � �������
try:
    DATDIR = sys.argv[1]
except IndexError:
    DATDIR='dat/3' 
    DATDIR = r'\\arhive\Public\Arseniy\�����-�\06 ����'
    DATDIR = r'\\arhive\Public\Arseniy\Shtil Decoder\3'

# ����� ����� �����
DATFILEMASK = '%s/374����_%i (%i)(K).dat'

# ������������ ��������� GnuGlot
GNUPLOT = r'gnuplot\gnuplot.exe' 

BitMap={
# ���������� �������: ���� 76543210
#        0      1      2      3      4      5      6      7
'K1':[(1,8 ),(1,7 ),(1,6 ),(1,5 ),(1,4 ),(1,3 ),(1,2 ),(1,1 )],
'K2':[(2,4 ),(2,3 ),(2,2 ),(2,1 ),(1,12),(1,11),(1,10),(1,9 )],
'K3':[(2,12),(2,11),(2,10),(2,9 ),(2,8 ),(2,7 ),(2,6 ),(2,5 )]
}

import HTMLHEAD
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

# �������� ����� � ��������, ��������� � Excel ��� ��������
K1LOG = HTML('%s/K1.html'%DATDIR,'����� 1 (row): %s'%DATDIR)
K2LOG = HTML('%s/K2.html'%DATDIR,'����� 2 (row): %s'%DATDIR)
K3LOG = HTML('%s/K3.html'%DATDIR,'����� 3 (row): %s'%DATDIR)

P1LOG = HTML('%s/P1.html'%DATDIR,'����� 1: %s'%DATDIR)
P1LOG.SubTitle='������ ��� 1'
print >>P1LOG,HTMLHEAD.P1LOG

P2LOG = HTML('%s/P2.html'%DATDIR,'����� 2: %s'%DATDIR)
P2LOG.SubTitle='������ ��� 2'
print >>P2LOG,HTMLHEAD.P2LOG

P3021LOG = HTML('%s/P3021.html'%DATDIR,'����� 3(0,21): %s'%DATDIR)
P3021LOG.SubTitle='������ ��� 3(0,21)'
print >>P3021LOG,HTMLHEAD.Pn021LOG

P3XLOG = HTML('%s/P3x.html'%DATDIR,'����� 3(x): %s'%DATDIR)
P3XLOG.SubTitle='������ ��� 3(x)'
print >>P3XLOG,HTMLHEAD.PnXLOG

P4021LOG = HTML('%s/P4021.html'%DATDIR,'����� 4(0,21): %s'%DATDIR)
P4021LOG.SubTitle='������ ��� 4(0,21)'
print >>P4021LOG,HTMLHEAD.Pn021LOG

P4XLOG = HTML('%s/P4x.html'%DATDIR,'����� 4(x): %s'%DATDIR)
P4XLOG.SubTitle='������ ��� 4(x)'
print >>P4XLOG,HTMLHEAD.PnXLOG

R12 = HTML('%s/Report12.html'%DATDIR,'����� �� ������� 1+2: %s'%DATDIR)
R12.SubTitle='����� �� ������� 1+2'
print >>R12,HTMLHEAD.R12

######################################################

import os,time,re,math

# �������� ���� ����
# sys.stdout=open('log.log','w')

print time.localtime()[:6],sys.argv
print '\nDATDIR "%s"\n'%DATDIR
print 'DATFILEMASK "%s"\n'%DATFILEMASK

def dump(dat):
    '������� ������ ����-�����'
    T=''
    for addr in range(len(dat)):
        if addr%0x10==0: T+='\n%.4X: '%addr
        T+='%.2X '%dat[addr]
    T+='\n'
    return T

def bgcolor(F):
    return {True:"lightgreen", False:"yellow"}[F]

############################
# ����� ����������
############################

class Statistics:
    '���������� �� ����� �������'
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
#         T+='<td>���</td>'
#         T+='<td>�����</td>'
#         T+='<td colspan=2>�����</td>'
#         T+='<td>�������������</td>'
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
#             x='�����'
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
# ������ �������������� ������
# ���������� � �������������� ������
############################

class BitStream:
    '1-������ �����'
    def __init__(self,i,j):
        # ��������� ����� .dat-������ �� �����
        self.i=i; self.j=j
        self.DatFileName = DATFILEMASK%(DATDIR,i,j)
        # ������ �����
        DatFile = open(self.DatFileName)
        Records = DatFile.readlines()
        DatFile.close()
        # ��������� ������ �����
        self.dat = map(lambda x:int(x.split()[1]),Records)
    def __str__(self):
        return '�������� %i:%i\t%s\t[%i]'%(\
            self.i,self.j,\
            self.DatFileName,\
            len(self))
    def __len__(self): return len(self.dat)
    def __getitem__(self,idx): return self.dat[idx]

############################
# ��������������� �������
############################

def HD(dat):
    'hexdump ������'
    return '[%s]'%(\
        reduce(lambda a,b:'%s %s'%(a,b),\
               map(lambda x:'%.2X'%x,dat)))

############################
# ������ ����� ������
############################

class Signatura:
    '���������'
    def __init__(self, DAT): self.DAT = DAT
    def __str__(self): return HD(self.DAT)
    len = 3
    pair = [0x55, 0xAA]

class AnyTime:
    '����� �������'
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
    '����� �����'
class BSKVU(AnyTime):
    '����� �����'

class MagnetField:
    '��������� ����'
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

class Termo:
    '�����������'
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

class Upit:
    '���������� �������'
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

class Shina:
    '����-������'
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
# ������ �������
############################

class Package:
    '����� ����� ���'
    len = 0x20
    def __init__(self, CH, ADDR, DAT, HTMLOG):
        self.CH = CH
        self.ADDR = ADDR
        self.DAT = DAT
        self.HTMLOG = HTMLOG
        # ������������� � ���������� ������ �� ������ ����
        self.SIGN = Signatura(self.DAT[0:3])
        self.N = self.DAT[3]
        try:
            self.Type = {0:1, 1:2, 2:3, 255:4}[self.DAT[0]]
        except KeyError:
            self.Type = self.DAT[0]
        self.N = self.DAT[3]
        self.CRC_H = self.DAT[30]
        self.CRC_L = self.DAT[31]
        self.XBYTE = self.DAT[Package.len:Package.len+Signatura.len]
        self.OK = self.isValid()
    def __str__(self):
        T = '\n<a name="%s">����� %s@%s\n' % (self.ADDR, self.ADDR, self.CH)
        T += '-' * 40 + dump(self.DAT) + '-' * 40 + '\n'
        T += '���������: %s\n' % self.SIGN
        T += '# �����: %s\n' % self.N
        T += '���: %s\n' % self.Type
        T += 'CRC_H: %s\n' % self.CRC_H
        T += 'CRC_L: %s\n' % self.CRC_L
        T += '����������: %s\n' % self.OK
        T += 'xbyte: %s\n' % HD(self.XBYTE)
        T += '-' * 40 + '\n'
        return T
    def htmlreport(self):
        # htmlog
        print >> self.HTMLOG, '<tr bgcolor="%s">' % bgcolor(self.OK)
        self.HTMLOG['td'] = self.CH
        self.HTMLOG['td'] = self.N
        print >> self.HTMLOG, \
            '<td><a href="%s.html#%s">#%s</a></td>' % (\
                self.CH, self.ADDR, self.ADDR)
    def html(self):
        T = '<tr bgcolor="%s">' % bgcolor(self.OK)
        T += '<td><a href="#%s">#%s</a></td>' % (self.ADDR, self.ADDR)
        T += reduce(lambda a, b:a + b, map(lambda x:'<td>%s</td>' % x, self.DAT))
        T += '</tr>\n'
        return T
    def isValid(self): return self.CRC() == (self.CRC_H << 8) | self.CRC_L
    def CRC(self): return sum(self.DAT[:32-2])
    
class Package1(Package):
    '����� ��� ����1'
    def __init__(self, CH, ADDR, DAT, HTMLOG):
        # ����� ������������ �����������
        Package.__init__(self, CH, ADDR, DAT, HTMLOG)
        # ������������� ����� ����������� ��� �����1
        self.time = ShtyrTime(self.DAT[4:7 + 1])
        self.BSKVU1 = BSKVU(self.DAT[8:11 + 1])
        self.BSKVU2 = BSKVU(self.DAT[12:15 + 1])
        self.DM1peak = MagnetField(self.DAT[16:20 + 1])
        self.DM2peak = MagnetField(self.DAT[21:25 + 1])
        self.Temp = Termo(self.DAT[26:29 + 1])
        # html
        self.htmlreport()
    def htmlreport(self):
        Package.htmlreport(self)
        # htmlog
        for i in [
            self.time,
            self.BSKVU1, self.BSKVU1,
            self.DM1peak.X, self.DM1peak.Y, self.DM1peak.Z,
            self.DM2peak.X, self.DM2peak.Y, self.DM2peak.Z,
            self.Temp.DM1, self.Temp.DM2, self.Temp.SHT
        ]: self.HTMLOG['td'] = i
        print >> self.HTMLOG, '</tr>'
        # R12
        print >> R12, '<tr bgcolor="%s">' % bgcolor(self.OK)
        R12['td'] = self.CH
        R12['td'] = self.N
        R12['td'] = self.Type
        print >> R12, \
            '<td><a href="%s.html#%s">#%s</a></td>' % (\
                self.CH, self.ADDR, self.ADDR)
        for i in [
            self.time,
            self.BSKVU1, self.BSKVU1,
            self.DM1peak.X, self.DM1peak.Y, self.DM1peak.Z,
            self.DM2peak.X, self.DM2peak.Y, self.DM2peak.Z,
            self.Temp.DM1, self.Temp.DM2, self.Temp.SHT
        ]: R12['td'] = i
        print >> R12, '</tr>'
    def __str__(self):
        # ����� ������� �����������
        T = Package.__str__(self)
        T += '����� �����: %s\n' % self.time
        T += '����� �����1: %s\n' % self.BSKVU1
        T += '����� �����2: %s\n' % self.BSKVU2
        T += '��� DM1: %s\n' % self.DM1peak
        T += '��� DM2: %s\n' % self.DM2peak
        T += '�����������: %s\n' % self.Temp
        T += '-' * 40 + '\n'
        return T

class Package3x(Package):
    '����� ��� ����3x'
    def __init__(self, CH, ADDR, DAT, HTMLOG):
        # ����� ������������ �����������
        Package.__init__(self, CH, ADDR, DAT, HTMLOG)
        # ������������� ����� ����������� ��� �����3x
        self.SubBlock = self.DAT[4]
        self.ADC = self.DAT[5:28 + 1]
        self.SRC = self.DAT[29]
        # html
        self.htmlreport()
    def htmlreport(self):
        Package.htmlreport(self)
        self.HTMLOG['td'] = self.SubBlock
        for i in self.ADC: self.HTMLOG['td'] = i
        self.HTMLOG['td'] = self.SRC
        print >> self.HTMLOG, '</tr>'

class Package4x(Package3x):
    '����� ��� ����4x'

class Package3021(Package):
    '����� ��� ����3(0,21)'
    def __init__(self, CH, ADDR, DAT, HTMLOG):
        # ����� ������������ �����������
        Package.__init__(self, CH, ADDR, DAT, HTMLOG)
        # ������������� ����� ����������� ��� �����3
        self.time = ShtyrTime(self.DAT[5:8 + 1])
        self.BSKVU1 = BSKVU(self.DAT[9:12 + 1])
        self.SubBlock = self.DAT[4]
        self.ADC = self.DAT[13:28+1]
        self.SRC = self.DAT[29]
        # html
        self.htmlreport()
    def htmlreport(self):
        Package.htmlreport(self)
        self.HTMLOG['td'] = self.SubBlock
        self.HTMLOG['td'] = self.time
        self.HTMLOG['td'] = self.BSKVU1
        for i in self.ADC: self.HTMLOG['td'] = i
        self.HTMLOG['td'] = self.SRC
        print >>self.HTMLOG,'</tr>'

class Package4021(Package3021):
    '����� ��� ����4(0,21)'

class Package2(Package):
    '����� ��� ����2'
    def __init__(self, CH, ADDR, DAT, HTMLOG):
        # ����� ������������ �����������
        Package.__init__(self, CH, ADDR, DAT, HTMLOG)
        # ������������� ����� ����������� ��� �����2
        self.Upit = Upit(self.DAT[4:7 + 1])
        self.DM1 = MagnetField(self.DAT[8:12 + 1]) 
        self.DM2 = MagnetField(self.DAT[13:17 + 1])
        self.SHINA = Shina(self.N, self.DAT[18:29 + 1]) 
        # html
        self.htmlreport()
    def htmlreport(self):
        Package.htmlreport(self)
        # htmlog
        for i in [
        self.Upit.MIN,self.Upit.MAX,self.Upit.MED,
        self.DM1.X,self.DM1.Y,self.DM1.Z,
        self.DM2.X,self.DM2.Y,self.DM2.Z,
        self.SHINA.SK1,self.SHINA.SK2,self.SHINA.SK3,
        self.SHINA.SK4,self.SHINA.SK5,self.SHINA.SK6
                  ]:
            P2LOG['td'] = i 
        print >>P2LOG,'</tr>'
        # R12
        print >> R12, '<tr bgcolor="%s">' % bgcolor(self.OK)
        R12['td'] = self.CH
        R12['td'] = self.N
        R12['td'] = self.Type
        print >> R12, \
            '<td><a href="%s.html#%s">#%s</a></td>' % (\
                self.CH, self.ADDR, self.ADDR)
        for i in [' ']*12+[
        self.Upit.MIN,self.Upit.MAX,self.Upit.MED,
        self.DM1.X,self.DM1.Y,self.DM1.Z,
        self.DM2.X,self.DM2.Y,self.DM2.Z,
        self.SHINA.SK1,self.SHINA.SK2,self.SHINA.SK3,
        self.SHINA.SK4,self.SHINA.SK5,self.SHINA.SK6
                  ]:
            R12['td'] = i 
        print >>R12,'</tr>'
    def __str__(self):
        # ����� ������� �����������
        T = Package.__str__(self)
        T += 'U �������: %s\n' % self.Upit
        T += 'DM1: %s\n' % self.DM1
        T += 'DM2: %s\n' % self.DM2
        T += '����-������: %s\n' % self.SHINA
        T += '-' * 40 + '\n'
        return T

class Channel:
    '�����: ����� �������� ������'
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
            if T[0] == 0: 
                P = Package1(self.ID, a, T, P1LOG)
            elif T[0] == 1: 
                P = Package2(self.ID, a, T, P2LOG)
            elif T[0] == 0xFF:
                if T[3] == 200:
                    if T[4] in (0,21):
                        P = Package3021(self.ID, a, T, P3021LOG)
                    else:
                        P = Package3x(self.ID, a, T, P3XLOG)
                elif T[3] == 201:
                    if T[4] in (0,21):
                        P = Package4021(self.ID, a, T, P4021LOG)
                    else:
                        P = Package4x(self.ID, a, T, P4XLOG)
                else:
                    P = Package(self.ID, a, T, None)
            else: P = Package(self.ID, a, T, None)
            self.PACKS.append(P)
    def packindex(self):
        '������������ ������� �������'
        self.INDEX = []
        for i in range(len(self.DAT) - Package.len - Signatura.len):
            if self.DAT[i + 1:i + 3] == Signatura.pair:
                self.INDEX += [i]
    def __str__(self):
        return '����� %s [%i ����, %i �������]' % (self.ID, self.SZ, len(self.INDEX))
    def html(self):
        T = '<table border=1 cellpadding=3>\n'
        for P in self.PACKS: T += P.html()
        T += '</table>\n'
        for P in self.PACKS: T += '<pre>%s</pre>\n' % P
        return T
    def packages(self): return self.PACKS
    def package(self, addr): return self.DAT[addr:addr + 32+3]
    def __iter__(self): return iter(self.INDEX)

# �������� ������� �� ������

DAT={}
for i in [1,2]:
    for j in range(1,12+1):
        DAT[(i,j)]=BitStream(i,j)
        print DAT[(i,j)]

print
K1 = Channel('K1', BitMap['K1']) ; print K1 ; K1LOG.SubTitle = K1 ; print >> K1LOG, K1.html()
K2 = Channel('K2', BitMap['K2']) ; print K2 ; K2LOG.SubTitle = K1 ; print >> K2LOG, K2.html()
K3 = Channel('K3', BitMap['K3']) ; print K3 ; K3LOG.SubTitle = K1 ; print >> K3LOG, K3.html()

print '.'
