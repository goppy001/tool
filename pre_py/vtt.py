#!/home/hoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import glob

target_file = glob.glob("merge*.csv")
tgt_file = target_file[0]

#ファイルを読み込む関数
#dataは2週間分として14日分を取得するようにしている
def read_file(target_file):
    r_file = pd.read_csv(target_file, index_col=0)
    r_file.reset_index()
    df_time = r_file.iloc[:, [0]].values
    df_data = r_file.iloc[:, 1:15]
    return df_time, df_data

#行方向の平均を計算
def calc_mean(df_data):
    df_mean = df_data.mean(axis=1)
    df_mean = pd.DataFrame(df_mean)
    df_mean = df_mean.values
    return df_mean

#行方向の標準偏差を計算
def calc_std(df_data):
    df_std = df_data.std(axis=1)
    df_std = pd.DataFrame(df_std)
    df_std = df_std.values
    return df_std

#μ±σを計算する
def calc_threshold(grade, df_data):
    df_mean = calc_mean(df_data)
    df_std  = calc_std(df_data)
    upper_threshold = df_mean + grade * df_std
    lower_threshold = df_mean - grade * df_std
    return upper_threshold, lower_threshold

#ディレクトリ存在チェック
def check_dir(path):
    if os.path.isdir(path):
        pass
    else:
        os.mkdir(path)


################################################
##本処理##
################################################
#μ±nσのn
#ファイルを読み込み時刻カラムとデータカラムのための配列を用意
#μ±nσをしきい値とするため各計算結果を配列に格納。nはcalc_thresholdの
#第一引数として使用
n = 1
df_time, df_data = read_file(tgt_file)
up_th, low_th = calc_threshold(n, df_data)

#concatしてひとつのデータフレームにまとめるために各ndarrayをデータフレーム化
df_time = pd.DataFrame(df_time)
up_th   = pd.DataFrame(up_th)
low_th  = pd.DataFrame(low_th)

dir_png = "png_μ±" + str(n) + "σ"
dir_csv = "csv_μ±" + str(n) + "σ"
check_png = check_dir("./" + dir_png)
check_csv = check_dir("./" + dir_csv)

#concat後のカラム名を決め打ちで指定
headerlist = ['time', 'data', 'up_th', 'low_th']

check_files = glob.glob("./trend_data_*.csv")

#各日時データとしきい値をグラフに描画するために各CSVに対してループ処理
for file in check_files:
    name, _ = os.path.splitext(os.path.basename(file))
    name = name.replace("trend_data_", "")
    df = pd.read_csv(file, index_col=0)
    data_col = df.iloc[:, [1]]
    df_new = pd.concat([df_time, data_col, up_th, low_th],axis=1)
    df_new.columns = headerlist
    out_csv = df_new.to_csv(dir_csv + "/thshld_" + name + ".csv")

    fig = plt.figure()
    fig.add_subplot(111)
    ax  = df_new.plot(y='data',color='b')
    ax2 = df_new.plot(y=['up_th','low_th'], color='r',alpha=0.8, lw=0.5,ax=ax)
    ax2.set_ylabel('data')
    ax2.set_xlabel('time=point')
    plt.title(name + " with " + "μ±" + str(n) + "σ")
    plt.savefig(dir_png + "/thshld_" + name + ".png")
    plt.close('all')
