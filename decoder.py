# -*- coding: cp1251 -*-
# ������� ������ ����� �2
######################################################

# ������� � �������
DATDIR='dat/3' 

# ����� ����� �����
DATFILEMASK = '%s/374����_%i (%i)(K).dat'

CHBT={
# ���������� �������: ���� 76543210
#        0      1      2      3      4      5      6      7
'K1':[(1,8 ),(1,7 ),(1,6 ),(1,5 ),(1,4 ),(1,3 ),(1,2 ),(1,1 )],
'K2':[(2,4 ),(2,3 ),(2,2 ),(2,1 ),(1,12),(1,11),(1,10),(1,9 )],
'K3':[(2,12),(2,11),(2,10),(2,9 ),(2,8 ),(2,7 ),(2,6 ),(2,5 )]
}

# �������� ����� � ��������, ��������� � Excel ��� ��������
HTML1 = open('%s/kadr1.html'%DATDIR,'w')
HTML2 = open('%s/kadr2.html'%DATDIR,'w')

######################################################

import os,sys,time,re,math

# �������� ���� ����
sys.stdout=open('log.log','w')

print >>HTML1,'<html><title>���� 1: %s</title>'%DATDIR
print >>HTML2,'<html><title>���� 2: %s</title>'%DATDIR

print time.localtime()[:6],sys.argv
print '\nDATDIR "%s"\n'%DATDIR
print 'DATFILEMASK "%s"\n'%DATFILEMASK

def dump(dat):
    '������� ������ ����-�����'
    T=''
    for addr in range(len(dat)):
        if addr%0x10==0: T+='\n%.4X\t'%addr
        T+='%.2X '%dat[addr]
    return T

############################

class Channel:
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
        return '����� %i:%i\t%s\t[%i]'%(\
            self.i,self.j,\
            self.DatFileName,\
            len(self))
    def __len__(self): return len(self.dat)
    def __getitem__(self,idx): return self.dat[idx]

# �������� ������� �� ������

DAT={}
for i in [1,2]:
    for j in range(1,12+1):
        DAT[(i,j)]=Channel(i,j)
        print DAT[(i,j)] 

############################

class ByteStream:
    '����� �������� ������'
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
        '������������ ������� �������'
        self.INDEX=[]
        for i in range(len(self.DAT)-31):
            if self.DAT[i+1:i+3]==[0x55,0xAA]:
                self.INDEX+=[i]
    def __str__(self): return '����� %s: %s'%(self.ID,self.BT)
    def packages(self): return self.INDEX
    def package(self,addr): return self.DAT[addr:addr+32]

print
K1=ByteStream('K1',CHBT['K1']) ; print K1
K2=ByteStream('K2',CHBT['K2']) ; print K2
K3=ByteStream('K3',CHBT['K3']) ; print K3

############# ��������������� ������� ###############

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

############# ������ ����� ����� ###############

class vDumpable:
    def dump(self): return HD(self.DAT)
    def __str__(self): return HD(self.DAT)
    def html(self): return '<td>%s</td>'%HD(self.DAT)

class Signatura(vDumpable):
    '���������'
    def __init__(self,dat):
        assert len(dat)==3
        self.DAT=dat
    def __str__(self): return self.dump()
class AnyTime(vDumpable):
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
class MagnetField(vDumpable):
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
    def module(self):
        return math.sqrt(self.X**2+self.Y**2+self.Z**2) 
    def html(self): 
        return '<td>%s</td><td>%s</td><td>%s</td>'%(\
            self.X,self.Y,self.Z)
class Termo(vDumpable):
    '�����������'
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

class Upit(vDumpable):
    '���������� �������'
    def __init__(self,dat):
        assert len(dat)==4
        self.DAT=dat
        self.MIN=0.0
        self.MED=0.0
        self.MAX=0.0
    def html(self): return '<td>%.2f</td><td>%.2f</td><td>%.2f</td>'%(\
        self.MIN,self.MED,self.MAX)
class Shina(vDumpable):
    '����-������'
    def __init__(self,dat):
        assert len(dat)==29-18+1
        self.DAT=dat

############# ����� ����� ###############

class Frame:
    '����� ����� ���'
    def __init__(self,ch,addr,block):
        assert len(block)==32
        self.CH=ch
        self.ADDR=addr
        self.DAT=block
        # ������������� � ���������� ������ �� ������ ����
        self.type       =self.DAT[0]+1
        self.signature  =Signatura( self.DAT[0:2+1] )
        self.blockN     =           self.DAT[3]
        self.CRC_H      =           self.DAT[30]
        self.CRC_L      =           self.DAT[31]
        self.Valid      = self.isValid()
    HL='-'*55
    def __str__(self):
        T='����� %i %s@%.4X\n'%(self.type,self.CH,self.ADDR)+self.HL
        T+=dump(self.DAT)
        T+='\n'+self.HL
        T+='\n���������:\t%s'%self.signature
        T+='\n� �����:\t%.2X'%self.blockN
        T+='\nCRC_H:\t\t%.2X'%self.CRC_H
        T+='\nCLC_L:\t\t%.2X'%self.CRC_L
        T+='\n����������:\t%s'%self.Valid
        return T+'\n'
    def isValid(self): return self.CRC()==(self.CRC_H<<8)|self.CRC_L
    def CRC(self): return sum(self.DAT[:-2])
    HTMLFOOTER='</table>'
    HEADBGCOLOR='#DDDDFF'

class Frame2(Frame):
    '����� ��� ����2'
    def __init__(self,ch,addr,block):
        Frame.__init__(self, ch, addr, block)
        # ������������� � ���������� ������ �� ������ ����
        self.Upit   = Upit(self.DAT[4:7+1])
        self.DM1    = MagnetField(self.DAT[8:12+1]) 
        self.DM2    = MagnetField(self.DAT[13:17+1])
        self.SHINA  = Shina(self.DAT[18:29+1]) 
    def __str__(self):
        T=Frame.__str__(self)
        T+='\nU �������\t%s'%self.Upit
        T+='\nDM1\t\t%s'%self.DM1
        T+='\nDM2\t\t%s'%self.DM2
        T+='\n����-������\t%s'%self.SHINA
        return T
    HTMLHEADER='''
<H1>���� 2</H1>
<table cellpadding=5 border=1>
<tr bgcolor='''+Frame.HEADBGCOLOR+'''>
<td rowspan=3>�����<br>�����</td>
<td rowspan=2 colspan=3>U �������<br>� ������</td>
<td colspan=6>��������� ���� � ������������</td>
<td rowspan=3>����<br>������</td>
</tr>
<tr bgcolor=#AAFFAA>
<td colspan=3>DM1</td>
<td colspan=3>DM2</td>
</tr>
<tr bgcolor=#AAFFAA>
<td>min</td>
<td>�������</td>
<td>max</td>
<td>X</td>
<td>Y</td>
<td>Z</td>
<td>X</td>
<td>Y</td>
<td>Z</td>
</tr>
'''
    def htmlValid(self): return {True:'',False:'bgcolor=#FFAAAA'}[self.Valid] 
    def html(self):
        return '''<tr %s><td><a href="#%i">%i</a></td>%s%s%s%s</tr>'''%(\
            self.htmlValid(),\
            self.blockN,self.blockN,\
            self.Upit.html(),\
            self.DM1.html(),self.DM2.html(),\
            self.SHINA.html()\
            )
    
class Frame1(Frame):
    '����� ��� ����1'
    def __init__(self,ch,addr,block):
        Frame.__init__(self, ch, addr, block)
        # ������������� � ���������� ������ �� ������ ����
        self.time       =ShtyrTime(     self.DAT[4:7+1])
        self.BSKVU1     =BSKVU(         self.DAT[8:11+1])
        self.BSKVU2     =BSKVU(         self.DAT[12:15+1])
        self.DM1peak    =MagnetField(   self.DAT[16:20+1])
        self.DM2peak    =MagnetField(   self.DAT[21:25+1])
        self.Temp       =Termo(         self.DAT[26:29+1])
    def checksum(self,addr): return sum(self.DAT[0,29+1])
    def __str__(self):
        T=Frame.__str__(self)
        T+='\n����� �����:\t%s\t\t%s'%(self.time.dump(),self.time)
        T+='\n�����1:\t\t%s\t\t%s'%(self.BSKVU1.dump(),self.BSKVU1)
        T+='\n�����2:\t\t%s\t\t%s'%(self.BSKVU2.dump(),self.BSKVU2)
        T+='\n��� DM1:\t%s\t%s'%(self.DM1peak.dump(),self.DM1peak)
        T+='\n��� DM2:\t%s\t%s'%(self.DM2peak.dump(),self.DM2peak)
        T+='\n�����������:\t%s'%self.Temp
        T+='\n'+self.HL
        return T
    HTMLHEADER='''
<H1>���� 1</H1>
<table cellpadding=5 border=1>
<tr bgcolor='''+Frame.HEADBGCOLOR+'''>
<td rowspan=3>�����<br>�����</td>
<td rowspan=2 colspan=3>�����, ��:��:��:��</td>
<td colspan=6>��������� ���� � ������������</td>
<td colspan=3 rowspan=2>�����������<br>� ����������������</td>
</tr>
<tr bgcolor=#AAFFAA>
<td colspan=3>DM1</td>
<td colspan=3>DM2</td>
</tr>
<tr bgcolor=#AAFFAA>
<td>�����</td>
<td>�����1</td>
<td>�����2</td>
<td>X</td>
<td>Y</td>
<td>Z</td>
<td>X</td>
<td>Y</td>
<td>Z</td>
<td>DM1</td>
<td>DM2</td>
<td>�����</td>
</tr>
'''
    def html(self):
        return '''<tr %s><td><a href="#%i">%i</a></td><td>%s</td><td>%s</td><td>%s</td>%s%s%s</tr>'''%(\
            {True:'',False:'bgcolor=#FFAAAA'}[self.Valid],
            self.blockN,self.blockN,\
            self.time,self.BSKVU1,self.BSKVU2,\
            self.DM1peak.html(),self.DM2peak.html(),
            self.Temp.html()
            )

############# ������ ������� K1..K3 �� ������ ###############

BLKSET1={}
BLKSET2={}
for K in [K1,K2,K3]:
    for P in K.packages():
        PACK=K.package(P)
        if PACK[0]+1==1:
            F=Frame1(K.ID,P,PACK) 
            BLKSET1[F.blockN]=F
        elif PACK[0]+1==2:
            F=Frame2(K.ID,P,PACK) 
            BLKSET2[F.blockN]=F
        else:
            F=Frame(K.ID,P,PACK)
        print '\n%s'%F

############# ��������� ������� ###############

print >>HTML1,Frame1.HTMLHEADER
print >>HTML2,Frame2.HTMLHEADER

for B in sorted(BLKSET1.keys()):
    BLK=BLKSET1[B]
    print >>HTML1,BLK.html()
print >>HTML1,Frame1.HTMLFOOTER
for B in sorted(BLKSET1.keys()):
    BLK=BLKSET1[B]
    print >>HTML1,'<a name="%s">\n<pre>\n%s\n</pre>\n</a>\n'%(BLK.blockN,BLK)

for B in sorted(BLKSET2.keys()):
    BLK=BLKSET2[B]
    print >>HTML2,BLK.html()
print >>HTML2,Frame2.HTMLFOOTER
for B in sorted(BLKSET2.keys()):
    BLK=BLKSET2[B]
    print >>HTML2,'<a name="%s">\n<pre>\n%s\n</pre>\n</a>\n'%(BLK.blockN,BLK)

print >>HTML1,'</html>'
print >>HTML2,'</html>'
