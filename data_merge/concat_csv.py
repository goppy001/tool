
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import glob


def check_file(tmpfile):
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    else:
        pass


files = glob.glob("*.csv")
headerlist = []
data_array = []
service_list = []
name_list = []

files = sorted(files, reverse=True)

for i, f in enumerate(files):
    # ファイル名から情報をアンダースコア区切りで情報を抽出
    name, _ = os.path.splitext(os.path.basename(f))
    hostname = name.split("_")[0]
    servicename = name.split("_")[1]
    serv_no = name.split("_")[2]
    status = name.split("_")[3]
    pace = name.split("_")[4]
    service_list = [servicename, serv_no]
    service = "_".join(service_list)
    # 事前に結合ファイル削除
    category = "all"
    all_list = [hostname, servicename, category, status, pace]
    rename = "_".join(all_list) + ".csv"
    check_file(rename)

    # pandas処理のためデータフレーム化
    df = pd.read_csv(f, index_col=None)
    datetime = df.iloc[:, 0].values
    data = df.iloc[:, 1].values
    headerlist.append(service)
    datalist.append(pd.DataFrame(data))
    # 最初のループでインデックスとなる時刻と時刻ヘッダを取り出す→別配列に格納
    if i == 0:
        headerlist.insert(0, "DATETIME")
        datalist.insert(0, pd.DataFrame(datetime))


df = pd.concat(datalist, axis=1)
df.columns = headerlist

df = pd.DataFrame(df)
df.sort_index(axis=1, ascending=True, inplace=True)

# 結合ファイルを出力
df.to_csv(rename)
