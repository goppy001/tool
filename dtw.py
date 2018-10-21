
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import glob
from itertools import product
import re
import shutil

def check_dir(dirpath):
    if os.path.isdir(dirpath):
        pass
    else:
        os.mkdir(dirpath)

target_dir = "./"
result_dir = "./result"
exception_dir = result_dir
check_dir(result_dir)

work_dir = "dtw"
work_dir = result_dir + "/" + work_dir
check_dir(work_dir)
dir_png = "png"
dir_png = work_dir + "/" + dir_png
check_dir(dir_png)


#####################################################
###メイン処理####
#####################################################

delta = lambda a, b: (a - b)** 2
first = lambda x: x[0]
second = lambda x: x[1]

#最小値を算出するための関数
def minval(val1, val2, val3):
    if first(val1) <= min(first(val2), first(val3)):
        return val1, 0
    elif first(val2) <= first(val3):
        return val2, 1
    else:
        return val3,2

#dtw距離の計算
def calc_dtw(A, B):
    S = len(A)
    T = len(B)
    m = [[0 for j in range(T)] for i in range(S)]
    m[0][0] = (delta(A[0], B[0]), (-1, -1))
    for i in range(1, S):
        m[i][0] = (m[i - 1][0][0] + delta(A[i], B[0]), (i - 1, 0))
    for j in range(1,T):
        m[0][j] = (m[0][j-1][0] + delta(A[0], B[j]), (0,j-1))

    for i in range(1,S):
        for j in range(1,T):
            minimum, index = minval(m[i-1][j], m[i][j-1], m[i-1][j-1])
            indexes = [(i-1,j), (i,j-1), (i-1,j-1)]
            m[i][j] = (first(minimum) + delta(A[i], B[j]), indexes[index])
    return m


target_file = "for_clustering.csv"
df = pd.read_csv(target_file, index_col=[0])
name, _ = os.path.splitext(os.path.basename(target_file))
df_data = df.iloc[:, 1:]
df_data = df_data.dropna()
dtw = []
for i, (key1, key2) in enumerate(product(df_data.columns, df_data.columns)):
    dtw.append(calc_dtw(df_data[key1].get_values(),df_data[key2].get_values())[-1][-1][0])
    print(key1 + " - " + key2, dtw[i])

dtw = np.array(dtw).reshape(len(df_data.columns), -1)

fig = plt.figure(figsize=(20,20))
ax = fig.add_subplot(111)
ax.set_aspect("equal")
plt.pcolor(dtw, cmap=plt.cm.Blues)
plt.xlim(xmax=len(df.columns)-1)
plt.ylim(ymax=len(df.columns)-1)
plt.xticks(np.arange(0.5, len(df.columns)+0.5), list(df.columns), rotation=90)
plt.yticks(np.arange(0.5, len(df.columns)+0.5), list(df.columns))
plt.colorbar()
plt.savefig(dir_png + "/dtw_" + name + ".png")
plt.close()


shutil.move(target_file, work_dir)