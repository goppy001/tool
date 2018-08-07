#!/home/glodia/.pyenv/versions/3.6.5/bin/python
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

filepath = "v5dcpoap-11_cpu_average_60sec_joined.csv"
monthlypath = glob.glob("./separated_cpu/*.csv")

#データセット読込
df = pd.read_csv(filepath, index_col=0, encoding="utf-8")

#グラフを生成する
df = df.reset_index()
df['DATETIME'] = pd.to_datetime(df['DATETIME'], format = '%Y/%m/%d %H:%M')
df['cpu0'] = df['cpu0'].values.astype(float)
df['year'] = df['DATETIME'].map(lambda x: x.year)
df['month'] = df['DATETIME'].map(lambda x: x.month)

sep_data = []
sep_date = []
sep_year = []
sep_month = []
last_data = []
last_date = []
df_datetime = df.DATETIME.values
df_cpu = df.cpu0.values
df_year = df.year.values
df_month = df.month.values

i = 0
j = 0

for idx in range(df.shape[0]):

        sep_data.append(df_cpu[idx])
        sep_date.append(df_datetime[idx])
        sep_year.append(df_year[idx])
        sep_month.append(df_month[idx])
 
        if len(sep_month) <= 1:
            i+=1
            continue

        if len(sep_month) > 1:
            if sep_month[i] - sep_month[i-1] == 0:
                i+=1
                continue

            if len(last_date) > 0:
                sep_data.insert(0, last_data[j])
                sep_date.insert(0, last_date[j])
                j+=1
            ym = str(sep_year[i-1]) + str(sep_month[i-1])
            new_data = pd.DataFrame({'DATETIME' : sep_date[:-1],
                                'cpu0' : sep_data[:-1]})
            df_new = new_data.to_csv("./separated_cpu/" + ym + ".csv")
            last_data.append(sep_data[-1])
            last_date.append(sep_date[-1])
            sep_data.clear()
            sep_date.clear()
            sep_year.clear()
            sep_month.clear()
            i=0

for monthly_file in monthlypath:
    name, ext = os.path.splitext(os.path.basename(monthly_file))
    new_df = pd.read_csv(monthly_file, index_col=0)
    new_df = new_df.reset_index()
    df['DATETIME'] = pd.to_datetime(df['DATETIME'], format= '%Y-%m-%d %H:%M')
    df['cpu0'] = df['cpu0'].values.astype(float)
    data = new_df.groupby('DATETIME')['cpu0'].sum().reset_index()
    data = data.set_index(['DATETIME'])
    
    data.plot()
    plt.savefig("./separated_cpu/row_" + name + ".png")
    plt.close()
    
    #トレンド成分抽出
    res = sm.tsa.seasonal_decompose(data.values, freq=1440)
    res.plot()
    plt.savefig("./separated_cpu/res_" + name + ".png")
    plt.close()

    trend = res.trend
    trend = pd.DataFrame({'trend': trend, 'DATETIME':data.index})
    trend['DATETIME'] = pd.to_datetime(trend['DATETIME'], format='%Y-%m-%d %H:%M')
    trend = trend.set_index(['DATETIME'])
    trend.plot()
    plt.savefig("./separated_cpu/trend_" + name + ".png")
    plt.close()
