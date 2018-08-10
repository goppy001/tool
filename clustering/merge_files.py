#!/home/hoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import glob
import re

files = glob.glob("./*_cpu.csv")
headerlist = []
datalist = []
tmpfile = "merged_data.csv"

if os.path.isfile(tmpfile):
    os.remove("./" + tmpfile)
else:
    pass


#各CSVをひとつのCSVにまとめて出力する
for file in files:
    name = re.sub(r'\D', '', file)
    headerlist.append(name)
    datalist.append(pd.read_csv(file, usecols=['cpu0']))
    
df = pd.concat(datalist, axis=1)
df.columns = headerlist
df.head()

df.to_csv(tmpfile)