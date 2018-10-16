#!/home/hogehoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import glob
import os

def check_dir(dirpath):
    if os.path.isdir(dirpath):
        pass
    else:
        os.mkdir(dirpath)

#窓関数を定義する
def embed(data, size):
    #空の多次元配列を用意
    window = np.empty((0, size))
    for idx in range(0, len(data)-size+1):
        new_window = [data[i] for i in range(idx, idx+size)]
        window = np.append(window, np.array([new_window]), axis=0)
    return window

dir_csv = "./sst_CSV"
dir_png = "./sst_PNG"
target_file = glob.glob("trend_cpu_20*.csv")


for file in target_file:
    df_all = pd.read_csv(file, index_col=0)
    df_all = df_all.dropna()
    name, _ = os.path.splitext(os.path.basename(file))
    data   = df_all.iloc[:,1].values
    """
    w : int
        Window size
    m : int
        Number of basis vectors
    k : int
        Number of columns for the trajectory and test matrices
    L : int
        Lag time
    """

    w = 60
    m = 2
    k = w/2
    L = k/2
    Tt = len(data)
    abnormality = np.zeros(Tt)

    for t in range(int(w+k), int(Tt-L+1)):
        #履歴行列
        begin_at = t-w-k+1
        end_at   = t-1
        x1 = pd.DataFrame(embed(data[int(begin_at):int(end_at)], w).T)
        x1 = x1.iloc[::-1]

        #テスト行列
        begin_at = t-w-k+1+L
        end_at   =  t-1+L
        x2 = pd.DataFrame(embed(data[int(begin_at):int(end_at)], w).T)
        x2 = x2.iloc[::-1]

        #履歴行列に対する特異値分解
        u1, s1, v1 = np.linalg.svd(x1, full_matrices=False)
        u1 = u1[:, 0:m]
        #テスト行列に対する特異値分解
        u2, s2, v2 = np.linalg.svd(x2, full_matrices=False)
        u2 = u2[:, 0:m]

        #部分空間同士（左特異行列）の重なり合いと異常度
        s = np.linalg.svd(np.dot(u1.T, u2), full_matrices=False, compute_uv=False)
        abnormality[t] = 1 - s[0] #最大特異値だけ必要なため第一要素を取る（特異値は対角成分のみ非負で大きい順に並ぶため）
    
    #変化度をmax1にするデータ整形
    mx = np.max(abnormality)
    abnormality = abnormality / mx
    new_data = pd.DataFrame(abnormality)
    check_dir(dir_csv)
    output_csv = new_data.to_csv(dir_csv + "/sst_" + name + "_.csv")

    #テストデータと異常度のプロット
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    p1, = ax1.plot(abnormality, '-b')
    ax1.set_ylabel('degre of change')
    ax1.set_ylim(0, 1.2)
    p2, = ax2.plot(data, '-g')
    ax2.set_ylabel('oveserved')
    plt.title("Singular Spectrum Transformation")
    ax1.legend([p1, p2], ["degree of change", "observed"])
    check_dir(dir_png)
    plt.savefig(dir_png + '/result_sst_' + name + '_.png')
    plt.close()
