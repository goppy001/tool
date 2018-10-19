
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import glob

#作業対象ファイル
old_category = "all"
#あたらしいなまえ
new_category = "ave"

def check_file(tmpfile):
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    else:
        pass

files = glob.glob("*.csv")
datalistall = []
datalist = []
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

    all_list = [hostname, servicename, new_category, status, pace]
    rename = "_".join(all_list) + ".csv"

    #allが入っているファイルが対象
    if serv_no == old_category:
        # pandas処理のためデータフレーム化
        df = pd.read_csv(f, index_col=0)
        datetime = df.iloc[:, 0].values
        data1 = df.iloc[:, 1].values
        data2 = df.iloc[:, 2].values
        data3 = df.iloc[:, 3].values
        data4 = df.iloc[:, 4].values
        datalistall.append([data1,data2,data3,data4])
        datalist = np.average(datalistall,axis=1)

        datetime = pd.DataFrame(datetime)
        datalist = pd.DataFrame(datalist)
        datalist = datalist.T

        df = pd.concat([datetime,datalist], axis=1)

        df = pd.DataFrame(df)
#        df = pd.DataFrame(df,columns=['DATETIME','cpu_average'])
        df.columns = ['DATETIME','cpu_average']

        # 結合ファイルを出力
        df.to_csv(rename)
