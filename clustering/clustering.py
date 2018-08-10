#!/home/hogehoge/.pyenv/versions/3.6.5/bin/python
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
z_files = glob.glob("./label*.csv")
headerlist = []
datalist = []
z_array = []
tmpfile = "merged_data.csv"

N_CLUSTERS = 5

#CSVを読み込んでクラスタリングする
df_all = pd.read_csv(tmpfile, index_col=0)
df_array = np.array(df_all).T
names= df_all.columns.values

z_array = np.array(sp.zscore(df_all)).T
z_array_df = z_array.T
z_names = names.T
df_all_z = pd.DataFrame(z_array_df, columns=z_names)

kmeans_model = KMeans(n_clusters=N_CLUSTERS, random_state=30).fit(df_array)
labels = kmeans_model.labels_

for i in range(N_CLUSTERS):
    tmparray = []
    for label, name in zip(labels, names):
        if i == label:
            tmparray.append(name)
    df_pickup = df_all[tmparray]
    df_pickup.to_csv("label" + str(i) + ".csv")
    plt.figure()
    df_pickup.plot(legend=False)
    plt.subplots_adjust(bottom=0.20)
    plt.title("Default_label_" + str(i))
    plt.savefig("label" + str(i) + ".png")
    plt.close('all')
    tmparray = []

for i in range(N_CLUSTERS):
    tmparray_z = []
    data_z = []
    for label,name in zip(labels, names):
        if i == label:
            tmparray_z.append(name)
    df_z = df_all_z[tmparray_z]
    df_z.to_csv("label_z" + str(i) + ".csv")
    plt.figure()
    df_z.plot(legend=False)
    plt.subplots_adjust(bottom=0.20)
    plt.title("zscore_label_" + str(i))
    plt.savefig("label_z" + str(i) + ".png")
    plt.close('all')
