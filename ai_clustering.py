#!/home/tgoto/.pyenv/versions/3.6.5/bin/python
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
import subprocess

filetype = "wholesale.csv"
pwd = os.getcwd() + "/"
outdir = pwd + "result/"
filepath=pwd + filetype

N_CLUSTERS = 4

#データセット読込
df = pd.read_csv(filepath, encoding="SHIFT-JIS")
df = df.dropna()
   
#日付と時刻を合体
#df.index = df.index.map(lambda x: dt.datetime.strptime(df.loc[x].DATE + " " + df.loc[x].TIME, "%Y-%m-%d %H:%M:%S"))

#データフレームからNumpyの行列に変換
df_array = np.array([df['Fresh'].tolist(),
                     df['Milk'].tolist(),
		     df['Grocery'].tolist(),
		     df['Frozen'].tolist(),
                     df['Detergents_Paper'].tolist(),
                     df['Delicassen'].tolist()],np.float32)

#df_arrayの転置行列
df_array = df_array.T
#クラスタ分析を実行
cls = KMeans(n_clusters=N_CLUSTERS)
pred = cls.fit_predict(df_array)

#元データにクラスタ番号を追加
#df.to_csv(outdir + "add_" + filetype)
#df_copy = pd.read_csv(outdir + "add_" + filetype, encoding="SHIFT-JIS")
#cmd = "sudo chmod -R 777 " + outdir
#subprocess.run(cmd.split()) 
df['cluster_id'] = pred
df.to_csv(outdir + "add_" + filetype)
#各クラスタに所属するサンプル数の分布
#df['cluster_id'].value_counts()

#グラフ化
plt.figure()

for i in range(N_CLUSTERS):
    labels = df_array[pred == i]
    plt.scatter(labels[:,0], labels[:,1])

#クラスタのセントロイド（重心）を描く
centers = cls.cluster_centers_
plt.scatter(centers[:, 0], centers[:,1], s=100,
        facecolors='none', edgecolors='black')

plt.savefig(outdir + filetype + ".png")
plt.close('all')


