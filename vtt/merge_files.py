
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import glob
import re
import datetime

exception_dir  = "./result"
target_dir = "./"
headerlist = []
datalist = []
tmp_list = []
d = 91
d_idx = d-1

#resultディレクトリ存在チェック作成
if os.path.isdir(exception_dir):
    pass
else:
    os.mkdir(exception_dir)

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
#各CSVをひとつのCSVにまとめて出力する
for i, file in enumerate(target_list):
    if size_list[i] < max(size_list):
        continue
    else:
        name, _ = os.path.splitext(os.path.basename(file))
        name    = name.replace("trend_cpu_", "")
        rename    = pd.to_datetime(name, format='%Y-%m-%d')
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
#上記ソートだけではだめなので文字型の日付をdatetime型に変換してリストに再代入
for file in tmp_list:
    name = pd.to_datetime(file, format='%Y-%m-%d')
    rename = '{d.year}-{d.month}-{d.day}'.format(d=name)
    re_list.append(rename)


#ディレクトリ名をソート
for file in dir_list:
    name = file.replace("./", "")
    name = pd.to_datetime(name, format='%Y-%m')
    rename = '{d.year}-{d.month}'.format(d=name)
    re_dir_list.append(rename)
red_dir_list = sorted(re_dir_list)

target_files = ["./" + re_dir_list[i] + "/trend_cpu_" + str(tf) + ".csv" for i, tf in enumerate(re_list)]

for i, f in enumerate(target_files):
    df = pd.read_csv(f, index_col=0)
    time = df.iloc[:,0].values
    data = df.iloc[:,1].values
    name, _ = os.path.splitext(os.path.basename(f))
    name    = name.replace("trend_cpu_", "")
    rename    = pd.to_datetime(name, format='%Y-%m-%d')
    rename_pattern = "(.*) (.*)"
    d = re.search(str(rename_pattern), str(rename))
    headerlist.append(d.group(1))
    #最初のループでインデックスとなる時刻と時刻ヘッダを取り出す→別配列に格納
    if i == 0:
        headerlist.insert(0,"TIME")
        datalist.append(pd.DataFrame(time))
        num_na = df.isnull().sum()
        #今後移動平均の範囲が変わった時ようにNaの数を数えるようにしている
        #このNaを前日データで埋めるため
        num_na = num_na.iloc[1].astype(int)
        prev_data=df.iloc[:,1].iloc[-num_na:]
        prev_data.reset_index()
        df_data = pd.DataFrame(data)
    if i > 0:
        df_data  = pd.concat([prev_data,df.iloc[:,1]], ignore_index=True).dropna()
        df_data  = df_data.values
        prev_data = df.iloc[:,1].iloc[-num_na:]
        prev_data.reset_index()
        df_data = pd.DataFrame(df_data)
    datalist.append(df_data)
    if i == d_idx:
        break
    
df = pd.concat(datalist, axis=1)
df.columns = headerlist

df = pd.DataFrame(df)
df.sort_index(axis=1, ascending=False, inplace=True)
df.to_csv("default_learn.csv")
