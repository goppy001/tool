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
import csv
import scipy.stats as sp

files = glob.glob("./*.csv")

N_CLUSTERS = 4

#データセット読込
def make_dataset(filepath):
    df = pd.read_csv(filepath, index_col=0, parse_dates=True, encoding="utf-8")
    df_array = np.array([df['cpu0'].tolist(),
                         df['cpu1'].tolist(),
                         df['cpu2'].tolist(),
                         df['cpu3'].tolist()],np.int32)
    df_array = df_array.T
    return df_array

#グラフを生成する
for file in files:
    df = make_dataset(file)
    print(df)
    df = sp.zscore(df)
    df = pd.DataFrame(df)
    plt.figure()
    df.plot()
    plt.savefig(file + ".png")
    plt.close()


