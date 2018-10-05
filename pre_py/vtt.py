#!/home/hogehoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import glob
import re

#データ抽出などに関するクラス
class extract:
    #ファイル名から名前を抽出する
    def ext_name(filepath, strg=None):
        #strg is optional string
        #exa): "hogehoge_" in "hogehoge_datetime.csv"
        name, _ = os.path.splitext(os.path.basename(filepath))
        if strg == None:
            pass
        else:
            name = name.replace(strg,"")
        return name

    #データフレームから時間カラムを取り出す
    def time(df):
        df_time = df.iloc[:, 0]
        return df_time

    #データフレームからd日間分のデータ部分を取り出す
    def ext_data(d, df):
        df_data = df.iloc[:, 1:d+1]
        return df_data


#統計量を定義しているクラス
class statistics:
    #一般的な算術平均を求める関数
    #列方向つまり各時刻の平均を取る
    def am(d, df):
        #am is arithmetic mean
        #d : days is for range of calc df_mean. int
        #    exa): d = 14
        #df : df is dataframe of pandas. pandas.DataFrame
        df_data   = df
        df_mean    = df_data.mean(axis=1)
        df_mean    = pd.DataFrame(df_mean)
        mean       = df_mean.values
        return mean

    #加重平均を求める（日数がそのまま重みとなる）
    def wma(d, df):
        df_data    = df
        nd_weight  = [i+1 for i in range(d)]
        nd_weight  = sorted(nd_weight, reverse=True)
        df_weight  = pd.DataFrame(nd_weight)
        #これをやらないと行列計算できない（おまじない）
        df_data.columns = df_weight.index   
        df_product = df_data.dot(df_weight)
        sum_weight = sum(nd_weight)
        df_wma     = df_product / sum_weight
        df_wma     = pd.DataFrame(df_wma)
        wma        = df_wma.values
        return wma

    #標準偏差を計算する
    def std(d, df):
        #d : days is for range of calc df_mean. int
        #    exa): d = 14
        #df : df is dataframe of pandas. pandas.DataFrame
        df_data = df
        df_std  = df_data.std(axis=1)
        df_std  = pd.DataFrame(df_std)
        std     = df_std.values
        return std

#閾値に関するクラス
class threshold:
    #μ±nσとする閾値を求める
    def threshold(n, d, learn_file, metric=None, service=None):
        #n is number of level of significance. int
        #learn_file is the csv file that used for calc mean and std.str
        df = pd.read_csv(learn_file, index_col=0)
        df_data = extract.ext_data(d, df)
        #平均計算はmetricで定義する
        if metric == 'None' or metric == 'am':
            df_mean = statistics.am(d, df_data)
        if metric == 'wma':
            df_mean = statistics.wma(d, df_data)
        df_std  = statistics.std(d, df_data)
        up_th = df_mean + n * df_std
        lw_th = df_mean - n * df_std
        if service == 'None':
            up_th = pd.DataFrame(up_th)
            lw_th = pd.DataFrame(lw_th)
        #引数（サービス名）によって上下限値を変更する実装
        #cpuの場合は使用率なので値域を[0,100]
        if service == 'cpu':
            up_th = np.where(up_th < 100, up_th, 100)
            lw_th = np.where(lw_th > 0, lw_th, 0)
            up_th = pd.DataFrame(up_th)
            lw_th = pd.DataFrame(lw_th)
        return up_th, lw_th

    #ファイルをマージする→閾値更新の際に使用
    def merge(d, target_file, df_data, learn_file, target_word=None):
        headerlist     = []
        datalist       = []
        df_target      = pd.read_csv(target_file, index_col=0)
        df_learn       = pd.read_csv(learn_file, index_col=0)
        df_data        = pd.DataFrame(df_data)
        df_time        = extract.time(df_target)
        df_learn_data  = extract.ext_data(d, df_learn)
        name_target    = extract.ext_name(target_file, strg=target_word)
        rename_target  = pd.to_datetime(name_target, format='%Y-%m-%d')
        df_learn_col_list = df_learn_data.columns.values.tolist()
        for col in df_learn_col_list:
            rename_learn = pd.to_datetime(col, format='%Y/%m/%d')
            rename_pattern = "(.*) (.*)"
            d = re.search(str(rename_pattern), str(rename_learn))
            headerlist.append(d.group(1))
        rename_target_pattern = "(.*) (.*)"
        d = re.search(str(rename_target_pattern), str(rename_target))
        headerlist.insert(0, d.group(1))
        headerlist.insert(0,'time')
        datalist.extend([df_data, df_learn_data])
        datalist.insert(0, df_time)
        df = pd.concat(datalist, axis=1)
        df.columns = headerlist
        df = pd.DataFrame(df)
        df.sort_index(axis=1, ascending=False, inplace=False)
        filename = "learn_" + str(name_target) + ".csv"
        df = pd.DataFrame(df)
        df.to_csv(filename)
        return filename

    #やっていることはマージだが閾値更新なのでupdateと再定義している
    def update(d, target_file, df_data, learn_file, target_word=None):
        learn_f = threshold.merge(d, target_file, df_data, learn_file, target_word)
        return learn_f

#閾値とデータをCSV化、グラフ化するためのクラス
class vtt:
    def vtt(n, d, learn_file, target_file, df_data, target_word=None, metric=None, service=None, makecsv=None, makefig=None):
        df_learn = pd.read_csv(learn_file, index_col=0)
        df_time  = extract.time(df_learn)
        up_th, lw_th = threshold.threshold(n, d, learn_file, metric, service)
        headerlist = ['time', 'data', 'up_th', 'lw_th']
        name = extract.ext_name(target_file, strg=target_word)
        data_col = pd.DataFrame(df_data)
        df_new = pd.concat([df_time, data_col, up_th, lw_th],axis=1)
        df_new.columns = headerlist
        df_new = pd.DataFrame(df_new)
        if makecsv == None or makecsv == True:
            out_csv = df_new.to_csv("thshld_" + name + ".csv")
        if makefig == None or makefig == True:
            fig = plt.figure()
            fig.add_subplot(111)
            ax  = df_new.plot(y='data',color='b')
            ax2 = df_new.plot(y=['up_th','lw_th'], color='g',alpha=0.8, lw=0.5,ax=ax)
            ax2.set_ylabel('cpu_use_rate')
            ax2.set_xlabel('time=point')
            plt.ylim(0,105)
            plt.title(name + " with " + "μ±" + str(n) + "σ")
            plt.savefig("thrshld_" + name + ".png")
            plt.close('all')
