
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import glob
import os
import re

def check_dir(dirpath):
    if os.path.isdir(dirpath):
        pass
    else:
        os.mkdir(dirpath)

target_dir = "./"
result_dir = "./result"
exception_dir = result_dir
check_dir(result_dir)

# 特定のディレクトリを対象外としてリストを構成する
target_files = []
if os.path.isdir(exception_dir):
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [
            d for d in dirs if exception_dir not in os.path.join(root, d)]
        targets = [os.path.join(root, f) for f in files]
        target_files.extend(targets)

size_list = []
target_list = []
for csvfile in target_files:
    name, ext = os.path.splitext(os.path.basename(csvfile))
    if ext == ".csv":
        df = pd.read_csv(str(csvfile), index_col=0)
        df_data = df.iloc[:, 1].values
        size_list.append(df_data.shape[0])
        target_list.append(csvfile)

dir_list = []
tmp_list = []
# 次元数調整（次元が小さい日時データはクラスタリングの対象外とする）
for i, file in enumerate(target_list):
    if size_list[i] < max(size_list):
        continue
    else:
        name, _ = os.path.splitext(os.path.basename(file))
        name = name.replace("trend_cpu_", "")
        rename = pd.to_datetime(name, format='%Y-%m-%d')
        rename_pattern = "(.*) (.*)"
        d = re.search(str(rename_pattern), str(rename))
        dd = d.group(1).split("-")
        ddl = [dd[0], dd[1]]
        date = "-".join(ddl)
        dir_name = os.path.dirname(file)
        dir_list.append(date)
        dir_list = sorted(dir_list)
        tmp_list.append(d.group(1))
        tmp_list = sorted(tmp_list)

re_list = []
re_dir_list = []
# 上記ソートだけではだめなので文字型の日付をdatetime型に変換してリストに再代入
for file in tmp_list:
    name = pd.to_datetime(file, format='%Y-%m-%d')
    rename = '{d.year}-{d.month}-{d.day}'.format(d=name)
    re_list.append(rename)

# ディレクトリ名をソート
for file in dir_list:
    name = file.replace("./", "")
    name = pd.to_datetime(name, format='%Y-%m')
    rename = '{d.year}-{d.month}'.format(d=name)
    re_dir_list.append(rename)
red_dir_list = sorted(re_dir_list)

target_files = ["./" + re_dir_list[i] + "/trend_cpu_" +
                str(tf) + ".csv" for i, tf in enumerate(re_list)]

######################################################################
###以下、メイン処理###
######################################################################

#窓関数を定義する
def embed(data, size):
    #空の多次元配列を用意
    window = np.empty((0, size))
    for idx in range(0, len(data)-size+1):
        new_window = [data[i] for i in range(idx, idx+size)]
        window = np.append(window, np.array([new_window]), axis=0)
    return window

work_dir = "sst"
work_dir = result_dir + "/" + work_dir
check_dir(work_dir)
dir_csv = work_dir + "/csv"
dir_png = work_dir + "/png"

for file in target_files:
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
    ax2.set_ylabel('trend')
    plt.title("Singular Spectrum Transformation")
    ax1.legend([p1, p2], ["degree of change", "trend"])
    check_dir(dir_png)
    plt.savefig(dir_png + '/result_sst_' + name + '_.png')
    plt.close()
