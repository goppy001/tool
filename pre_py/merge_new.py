#!/home/hoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import datetime as dt
import glob

files = glob.glob("trend_cpu*.csv")
headerlist = []
datalist = []
time = []

def check_file(tmpfile):
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    else:
        pass

#各CSVをひとつのCSVにまとめて出力する
for i, file in enumerate(files):
    name, _ = os.path.splitext(os.path.basename(file))
    name    = name.replace("trend_cpu_", "")
    name    = pd.to_datetime(name, format='%Y-%m-%d')
    year    = name.year
    month   = name.month
    tmpfile = "merged_" + str(year) + "-" + str(month) + ".csv"
    check_f = check_file(tmpfile)
    headerlist.append(str(name).replace("00:00:00", ""))
    readfile = pd.read_csv(file, index_col=0)
    if i == 0:
        headerlist.insert(0,"TIME")
        datalist.append(pd.DataFrame(readfile.iloc[:,[0]].values))
    readfile.dropna()
    data     =  pd.DataFrame(readfile.iloc[:, [1]].values)
    datalist.append(data)

df = pd.concat(datalist, axis=1)
df.columns = headerlist
df = pd.DataFrame(df)
df.sort_index(axis=1, ascending=False, inplace=True)
df.to_csv(tmpfile)
