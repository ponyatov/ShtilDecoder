# -*- coding: cp1251 -*-
# Декодер файлов Штиля №2

import os,sys,time,re

DATDIR = 'dat/1'

# генерация набора имен файлов
for i in [1,2]:
    for j in range(1,12):
        print '373ШИМП_%i(%i).dat'%(i,j)
