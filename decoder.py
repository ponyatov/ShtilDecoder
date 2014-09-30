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

######################################################

import os,sys,time,re

# �������� ���� ����
sys.stdout=open('log.log','w')

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
        return '����� %i:%i [%s] sz=%i'%(\
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
            if self.DAT[i:i+2]==[0x55,0xAA]:
                if self.isOkpacket(i):
                    self.INDEX+=[i]
    def isOkpacket(self,addr):
        CH,CL=self.DAT[addr+30:addr+30+2]
        return self.checksum(addr) == CH*0x100+CL
    def checksum(self,addr):
        '���������� ����������� ����� ������ ������������� � ������ addr'
        return sum(self.DAT[addr:addr+29+1])
    def __str__(self):
        T='����� %s: %s'%(self.ID,self.BT)
#         T+=dump(self.DAT)
        return T
    def packages(self): return self.INDEX
    def package(self,addr): return self.DAT[addr:addr+32]

print
K1=ByteStream('K1',CHBT['K1']) ; print K1
K2=ByteStream('K2',CHBT['K2']) ; print K2
K3=ByteStream('K3',CHBT['K3']) ; print K3

############################

class Package:
    '�����'
    def __init__(self,ch,addr,block):
        assert len(block)==32
        self.CH=ch
        self.ADDR=addr
        self.DAT=block
        # �������������
        self.signature=self.DAT[0:2+1]
        self.blockN=self.DAT[3]
        self.time=self.DAT[4:7+1]
        self.BSKVU1=self.DAT[8:11+1]
        self.BSKVU2=self.DAT[12:15+1]
        self.DM1peak=self.DAT[16:20+1]
        self.DM2peak=self.DAT[21:25+1]
        self.Temp=self.DAT[26:29+1]
        self.CRC_H=self.DAT[30]
        self.CRC_L=self.DAT[31]
    def checksum(self,addr): return sum(self.DAT[0,29+1])
    def __str__(self):
        HL='-'*55
        T='����� %s@%.4X\n'%(self.CH,self.ADDR)+HL
        T+=dump(self.DAT)
        T+='\n'+HL
        T+='\n���������:\t\t%s'%self.signature
        T+='\n� �����:\t\t%s'%self.blockN
        T+='\n����� �����:\t%s'%self.time
        T+='\n�����1:\t\t\t%s'%self.BSKVU1
        T+='\n�����2:\t\t\t%s'%self.BSKVU2
        T+='\n��� DM1:\t\t%s'%self.DM1peak
        T+='\n��� DM2:\t\t%s'%self.DM2peak
        T+='\n�����������:\t%s'%self.Temp
        T+='\nCRC_H:\t\t\t%s'%self.CRC_H
        T+='\nCLC_L:\t\t\t%s'%self.CRC_L
        T+='\n'+HL
        return T

for K in [K1,K2,K3]:
    for P in K.packages():
        print
        print Package(K.ID,P,K.package(P))
