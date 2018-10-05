#!/home/hogehoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import datetime as dt
import glob
import csv
import scipy.stats as sp
import statsmodels.api as sm

filepath  = "base_data_file.csv"

#データセット読込
df = pd.read_csv(filepath, index_col=0)
df = df.reset_index()
df['DATETIME'] = pd.to_datetime(df['DATETIME'], format = '%Y/%m/%d %H:%M')
df['cpu0']     = df['cpu0'].values.astype(float)
#日時データを年と月に分ける
df['year']     = df['DATETIME'].map(lambda x: x.year)
df['month']    = df['DATETIME'].map(lambda x: x.month)

#後述処理で使う空配列を作成
sep_date  = []
sep_data  = []
sep_year  = []
sep_month = []

last_date = []
last_data = []

#各カラムの値を取得
df_datetime = df.DATETIME.values
df_cpu      = df.cpu0.values
df_year     = df.year.values
df_month    = df.month.values

#カウンタ用変数
i = 0
j = 0

#月と日でCSVを切り分けるためのループ処理
#全行数でループ開始
for idx in range(df.shape[0]):
    #上記で用意した配列に1ループごとに値を格納する
    sep_data.append(df_cpu[idx])
    sep_date.append(df_datetime[idx])
    sep_year.append(df_year[idx])
    sep_month.append(df_month[idx])

    #差分を取るため最低2要素必要
    #要素が1つしかないなら差分は取れないのでcontinueで次のループに移行する
    if len(sep_month) <= 1:
        i+=1
        continue
    #要素が2つ以上あれば現在値と一つ前の値で差分を取る
    #差分が0ならその要素は同じ月であるといえる
    if len(sep_month) > 1:
        if sep_month[i] - sep_month[i-1] == 0:
            if idx+1 != df.shape[0]:
                i+=1
                continue
            else:
                pass
        #日付調整のために各配列の最終要素だけを格納したlast_dateを評価
        #1回目のループでは要素は0
        #もし要素が一つ以上あれば、現在ループしている配列の先頭にデータと日付を挿入する
        if len(last_date) > 0:
            sep_data.insert(0, last_data[j])
            sep_date.insert(0, last_date[j])
            j+=1
        ym = str(sep_year[i-1]) + "-" + str(sep_month[i-1])
        #ループ途中であれば要素の一つ前（先月末分）までを配列に格納
        if idx+1 != df.shape[0]:
            monthly_data = pd.DataFrame({'DATETIME' : sep_date[:-1],
                                         'cpu0' : sep_data[:-1]})
        #ループ最期であればすべての要素を配列に格納（月途中での処理を想定)
        if idx+1 == df.shape[0]:
            monthly_data = pd.DataFrame({'DATETIME' : sep_date[:],
                                         'cpu0' : sep_data[:]})
        df_monthly = monthly_data.to_csv("./separated_cpu/monthly/" + ym + ".csv")
        #現在ループしている配列の最終要素をlast_に追加する
        last_data.append(sep_data[-1])
        last_date.append(sep_date[-1])
        sep_data.clear()
        sep_date.clear()

        sep_year.clear()
        sep_month.clear()
        i=0

#以下は1日ごとのCSVに分割するためのループ
#動作原理は上記と同じ為割愛
monthlypath = glob.glob("./separated_cpu/monthly/20*.csv")
for monthly_file in monthlypath:
    df_m = pd.read_csv(monthly_file, index_col=0)
    df_m = df_m.reset_index()
    df_m['DATETIME'] = pd.to_datetime(df_m['DATETIME'], format = '%Y-%m-%d %H:%M')
    df_m['cpu0']     = df_m['cpu0'].values.astype(float)
    df_m['year']     = df_m['DATETIME'].map(lambda x: x.year)
    df_m['month']    = df_m['DATETIME'].map(lambda x: x.month)
    df_m['day']      = df_m['DATETIME'].map(lambda x: x.day)
    df_m['hour']     = df_m['DATETIME'].map(lambda x: x.hour)
    df_m['minute']   = df_m['DATETIME'].map(lambda x: x.minute)
    df_m['time']     = df_m[['hour', 'minute']].apply(lambda x: '{}:{}'.format(x[0], x[1]), axis=1)

    sep_year  = []
    sep_month = []
    sep_hour  = []
    sep_minute = []
    sep_time   = []

    sep_date  = []
    sep_data  = []
    sep_day   = []

    last_time = []
    last_data = []

    df_m_date  = df_m.DATETIME.values
    df_m_data  = df_m.cpu0.values
    df_m_year  = df_m.year.values
    df_m_month = df_m.month.values
    df_m_time  = df_m.time.values
    df_m_day   = df_m.day.values

    i = 0
    j = 0

    for idx in range(df_m.shape[0]):

        sep_date.append(df_m_date[idx])
        sep_data.append(df_m_data[idx])
        sep_year.append(df_m_year[idx])
        sep_month.append(df_m_month[idx])
        sep_time.append(df_m_time[idx])
        sep_day.append(df_m_day[idx])

        if len(sep_day) <= 1:
            i+=1
            continue
        if len(sep_day) > 1:
            if sep_day[i] - sep_day[i-1] == 0:
                if idx+1 != df_m.shape[0]:
                    i+=1
                    continue
                else:
                    pass
            if len(last_time) > 0:
                sep_time.insert(0, last_time[j])
                sep_data.insert(0, last_data[j])
                j+=1
            day = str(sep_year[i]) + "-" + str(sep_month[i]) + "-" + str(sep_day[i-1])
            ##トレンドファイル保存用のディレクトリ作成
            if os.path.isdir("./separated_cpu/daily/trend/" + str(sep_year[i]) + "-" + str(sep_month[i])):
                pass
            else:
                os.mkdir("./separated_cpu/daily/trend/" + str(sep_year[i]) + "-" + str(sep_month[i]))

            if idx+1 != df_m.shape[0]:
                daily_data = pd.DataFrame({'DATETIME' : sep_time[:-1],
                                           'cpu0' : sep_data[:-1]})
            if idx+1 == df_m.shape[0]:
                daily_data = pd.DataFrame({'DATETIME' : sep_time[:],
                                           'cpu0' : sep_data[:]})
            daily_data = daily_data.rename(columns={'cpu0': day})
            df_daily = daily_data.to_csv("./separated_cpu/daily/cpu_" + day + ".csv")
            last_time.append(sep_time[-1])
            last_data.append(sep_data[-1])
            sep_data.clear()
            sep_time.clear()
            sep_year.clear()
            sep_month.clear()
            sep_day.clear()
            i=0

dailypath = glob.glob("./separated_cpu//daily/cpu_*.csv")

#日時CSVの移動平均を取る
#移動平均のCSVの日時は%H:%mになる
for dailyfile in dailypath:
    df        = pd.read_csv(dailyfile, index_col=0)
    df_data   = pd.Series(list(df.iloc[:, 1].values))
    name, _   = os.path.splitext(os.path.basename(dailyfile))
    name      = name.replace("cpu_", "")
    df_time   = df.DATETIME.values
    df_ma     = df_data.rolling(15, center=False).mean().values
    df_new    = pd.DataFrame({'time' : df_time[:],
                              name   : df_ma[:]})
    name_for_dir = name.split('-')
    year    = name_for_dir[0]
    month   = name_for_dir[1]
    save_dir = "./separated_cpu/daily/trend/" + str(year) + "-" + str(month)
    make_csv = df_new.to_csv(save_dir + "/trend_cpu_" + str(name) + ".csv")
