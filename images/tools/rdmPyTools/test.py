# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 14:03:16 2021

@author: PieterDV
"""
import generalUtils as gu
import os
import re

its = ["LIRIAS987654321","123Lirias456","lirias1234545","Lirias4566","1234Lirias"]
for it in its:
    itnew = re.sub('^lirias','',it,flags=re.IGNORECASE)
    print(it+'->'+itnew)


dt = gu.get_yyyymmddOffset(-100)
print(dt)
dt = gu.get_yyyymmdd()
print(dt)

print ("Is it Directory?" + str(os.path.isdir('guru99.txt')))
print ("Is it Directory?" + str(os.path.isdir('c:/temp/rdm/')))