#!/home/glodia/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import datetime as dt
import glob
import re
import scipy.stats as sp

files = glob.glob("./*_cpu.csv")
headerlist = []
datalist = []
tmpfile = "merged_data.csv"

N_CLUSTERS = 4

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

#if not os.path.isdir("./label*"):
#    for i in range(N_CLUSTERS):
#        os.mkdir("./label" + str(i))
#else:
#    pass

#CSVを読み込んでクラスタリングする
df_all = pd.read_csv(tmpfile, index_col=0)
df_array = np.array(df_all).T

print(df_array.shape)

kmeans_model = KMeans(n_clusters=N_CLUSTERS, random_state=30).fit(df_array)
labels = kmeans_model.labels_
names = df.columns.values
tmparray = []
header = []

for i in range(N_CLUSTERS):
    for label, name in zip(labels, names):
        if i == label:
            tmparray.append(name)
    df_pickup = df_all[tmparray]
    plt.figure()
    df_pickup.plot(legend=False)
    plt.subplots_adjust(bottom=0.20)
    plt.legend(loc="best")
    plt.savefig("label" + str(i) + ".png")
    plt.close()
    tmparray = []

