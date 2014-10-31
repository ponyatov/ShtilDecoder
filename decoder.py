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

# �������� ����� � ��������, ��������� � Excel ��� ��������
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

# �������� ���� ����
# sys.stdout=open('log.log','w')

print >>HTML1,'<html><title>���� 1: %s</title>'%DATDIR
print >>HTML2,'<html><title>���� 2: %s</title>'%DATDIR
print >>HTML3,'<html><title>���� 3: %s</title>'%DATDIR
print >>HTML4,'<html><title>���� 4: %s</title>'%DATDIR
print >>HTMLS,'<html><title>����������: %s</title>'%DATDIR
print >>K1LOG,'<html>'
print >>K2LOG,'<html>'
print >>K3LOG,'<html>'

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

# �������� ������� �� ������

DAT={}
for i in [1,2]:
    for j in range(1,12+1):
        DAT[(i,j)]=BitStream(i,j)
        print DAT[(i,j)]

############################
# ��������������� �������
############################

def BF(dat,base,bitdef):
    '������ ������� �����'
    N=0
    for i in bitdef:
        BYTE,BITS=i ; BYTE-=base
        for b in range(BITS[0],BITS[1]+1):
            N=(N<<1)|(dat[BYTE]>>(8-b))&1
    return N

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
    def __init__(self,DAT): self.DAT=DAT
    def __str__(self): return HD(self.DAT)

class AnyTime:
    '����� �������'
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
    '����� �����'
class BSKVU(AnyTime):
    '����� �����'

class MagnetField:
    '��������� ����'
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
    '�����������'
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
    '���������� �������'
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
    '����-������'
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
# ������ �������
############################

class Package:
    '����� ����� ���'
    def __init__(self,CH,ADDR,DAT):
        self.CH = CH
        self.ADDR = ADDR
        self.DAT = DAT
        # ������������� � ���������� ������ �� ������ ����
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
        T='\n<a name="%s">����� %s@%s\n'%(self.ADDR,self.ADDR,self.CH)
        T+='-'*40+dump(self.DAT)+'-'*40+'\n'
        T+='���������: %s\n'%self.SIGN
        T+='# �����: %s\n'%self.N
        T+='���: %s\n'%self.Type
        T+='CRC_H: %s\n'%self.CRC_H
        T+='CRC_L: %s\n'%self.CRC_L
        T+='����������: %s\n'%self.OK
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
    '����� ��� ����1'
    def __init__(self,CH, ADDR, DAT):
        # ����� ������������ �����������
        Package.__init__(self, CH, ADDR, DAT)
        # ������������� ����� ����������� ��� �����1
        self.time    =ShtyrTime(  self.DAT[4:7+1])
        self.BSKVU1  =BSKVU(      self.DAT[8:11+1])
        self.BSKVU2  =BSKVU(      self.DAT[12:15+1])
        self.DM1peak =MagnetField(self.DAT[16:20+1])
        self.DM2peak =MagnetField(self.DAT[21:25+1])
        self.Temp    =Termo(      self.DAT[26:29+1])
    def __str__(self):
        # ����� ������� �����������
        T=Package.__str__(self)
        T+='����� �����: %s\n'%self.time
        T+='����� �����1: %s\n'%self.BSKVU1
        T+='����� �����2: %s\n'%self.BSKVU2
        T+='��� DM1: %s\n'%self.DM1peak
        T+='��� DM2: %s\n'%self.DM2peak
        T+='�����������: %s\n'%self.Temp
        T+='-'*40+'\n'
        return T

class Package2(Package):
    '����� ��� ����2'
    def __init__(self,CH, ADDR, DAT):
        # ����� ������������ �����������
        Package.__init__(self, CH, ADDR, DAT)
        # ������������� ����� ����������� ��� �����2
        self.Upit  = Upit(self.DAT[4:7+1])
        self.DM1   = MagnetField(self.DAT[8:12+1]) 
        self.DM2   = MagnetField(self.DAT[13:17+1])
        self.SHINA = Shina(self.N,self.DAT[18:29+1]) 
    def __str__(self):
        # ����� ������� �����������
        T=Package.__str__(self)
        T+='U �������: %s\n'%self.Upit
        T+='DM1: %s\n'%self.DM1
        T+='DM2: %s\n'%self.DM2
        T+='����-������: %s\n'%self.SHINA
        T+='-'*40+'\n'
        return T

class Channel:
    '�����: ����� �������� ������'
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
        '������������ ������� �������'
        self.INDEX=[]
        for i in range(len(self.DAT)-31):
            if self.DAT[i+1:i+3]==[0x55,0xAA]:
                self.INDEX+=[i]
    def __str__(self):
        return '����� %s [%i ����, %i �������]'%(self.ID,self.SZ,len(self.INDEX))
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

# ############# ������ ����� ����� ###############
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
# ############# ����� ����� ###############
# 
# class Frame:
#     def __init__(self,ch,addr,block):
#         # ���������� ����������
#         STATBROK[('c','obs')] += 1
#         STATBROK[(self.type,'obs')] += 1
#         if not self.Valid: 
#             STATBROK[('c','bit')] +=1
#             STATBROK[(self.type,'bit')] +=1
#     HTMLFOOTER='</table>'
#     HEADBGCOLOR='#DDDDFF'
# 
# class Frame4(Frame):
#     '����� ��� ����4'
#     def html(self): return '<tr><td>%s</td><td></td><td></td><td></td></tr>'%self.blockN
#     HTMLHEADER='''
# <H1>���� 4</H1>
# <table cellpadding=5 border=1>
# <tr bgcolor='''+Frame.HEADBGCOLOR+'''>
# <td>�����<br>�����</td>
# <td>�����</td>
# <td>��������<br>���������</td>
# <td>� ��������</td>
# <td>������� ���</td>
# </tr>
# '''
# 
# class Frame3(Frame):
#     '����� ��� ����3'
#     def html(self): return '<tr><td>%s</td><td></td><td></td><td></td></tr>'%self.blockN
#     HTMLHEADER='''
# <H1>���� 3</H1>
# <table cellpadding=5 border=1>
# <tr bgcolor='''+Frame.HEADBGCOLOR+'''>
# <td>�����<br>�����</td>
# <td>�����</td>
# <td>� ��������</td>
# <td>������� ���</td>
# </tr>
# '''
# # <tr bgcolor=#AAFFAA>
# # <td colspan=3>DM1</td>
# # <td colspan=3>DM2</td>
# # </tr>
# # <tr bgcolor=#AAFFAA>
# # <td>min</td>
# # <td>�������</td>
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
#     '����� ��� ����2'
#     def __init__(self,ch,addr,block):
#         Frame.__init__(self, ch, addr, block)
#         # ������������� � ���������� ������ �� ������ ����
#     def __str__(self):
#         T=Frame.__str__(self)
#         return T
#     HTMLHEADER='''
# <H1>���� 2</H1>
# <table cellpadding=5 border=1>
# <tr bgcolor='''+Frame.HEADBGCOLOR+'''>
# <td rowspan=3>�����<br>�����</td>
# <td rowspan=2 colspan=3>U �������<br>� ������</td>
# <td colspan=6>��������� ���� � ������������</td>
# <td rowspan=3>����<br>������</td>
# </tr>
# <tr bgcolor=#AAFFAA>
# <td colspan=3>DM1</td>
# <td colspan=3>DM2</td>
# </tr>
# <tr bgcolor=#AAFFAA>
# <td>min</td>
# <td>�������</td>
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
# <H1>���� 1</H1>
# <table cellpadding=5 border=1>
# <tr bgcolor='''+Frame.HEADBGCOLOR+'''>
# <td rowspan=3>�����<br>�����</td>
# <td rowspan=2 colspan=3>�����, ��:��:��:��</td>
# <td colspan=6>��������� ���� � ������������</td>
# <td colspan=3 rowspan=2>�����������<br>� ����������������</td>
# </tr>
# <tr bgcolor=#AAFFAA>
# <td colspan=3>DM1</td>
# <td colspan=3>DM2</td>
# </tr>
# <tr bgcolor=#AAFFAA>
# <td>�����</td>
# <td>�����1</td>
# <td>�����2</td>
# <td>X</td>
# <td>Y</td>
# <td>Z</td>
# <td>X</td>
# <td>Y</td>
# <td>Z</td>
# <td>DM1</td>
# <td>DM2</td>
# <td>�����</td>
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
# ############# ������ ������� K1..K3 �� ������ ###############
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
# ############# ��������� ������� ###############
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
