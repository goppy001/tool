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

filepath  = "hogehoge.csv"
dailypath = glob.glob("./separated_cpu//daily/*.csv")
hourspath = glob.glob("./separated_cpu/hours/*.csv")

#データセット読込
df = pd.read_csv(filepath, index_col=0)
df = df.reset_index()
df['DATETIME'] = pd.to_datetime(df['DATETIME'], format = '%Y/%m/%d %H:%M')
df['cpu0']     = df['cpu0'].values.astype(float)
df['year']     = df['DATETIME'].map(lambda x: x.year)
df['month']    = df['DATETIME'].map(lambda x: x.month)

sep_date  = []
sep_data  = []
sep_year  = []
sep_month = []

last_date = []
last_data = []

df_datetime = df.DATETIME.values
df_cpu      = df.cpu0.values
df_year     = df.year.values
df_month    = df.month.values

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
            ym = str(sep_year[i-1]) + "-" + str(sep_month[i-1])
            monthly_data = pd.DataFrame({'DATETIME' : sep_date[:-1],
                                'cpu0' : sep_data[:-1]})
            df_monthly = monthly_data.to_csv("./separated_cpu/monthly/" + ym + ".csv")
            last_data.append(sep_data[-1])
            last_date.append(sep_date[-1])
            sep_data.clear()
            sep_date.clear()
            sep_year.clear()
            sep_month.clear()
            i=0

monthlypath = glob.glob("./separated_cpu/monthly/*.csv")
for monthly_file in monthlypath:
    df_m = pd.read_csv(monthly_file, index_col=0)
    df_m = df_m.reset_index()
    df_m['DATETIME'] = pd.to_datetime(df_m['DATETIME'], format = '%Y-%m-%d %H:%M')
    df_m['cpu0']     = df_m['cpu0'].values.astype(float)
    df_m['year']     = df_m['DATETIME'].map(lambda x: x.year)
    df_m['month']    = df_m['DATETIME'].map(lambda x: x.month)
    df_m['day']      = df_m['DATETIME'].map(lambda x: x.day)
    df_m['hour']     = df_m['DATETIME'].map(lambda x: x.hour)

    sep_year  = []
    sep_month = []
    sep_date  = []
    sep_data  = []
    sep_day   = []

    last_date = []
    last_data = []

    df_m_date  = df_m.DATETIME.values
    df_m_data  = df_m.cpu0.values
    df_m_year  = df_m.year.values
    df_m_month = df_m.month.values
    df_m_day   = df_m.day.values

    i = 0
    j = 0
    for idx in range(df_m.shape[0]):

        sep_date.append(df_m_date[idx])
        sep_data.append(df_m_data[idx])
        sep_year.append(df_m_year[idx])
        sep_month.append(df_m_month[idx])
        sep_day.append(df_m_day[idx])

        if len(sep_day) <= 1:
            i+=1
            continue
        if len(sep_day) > 1:
            if sep_day[i] - sep_day[i-1] == 0:
                i+=1
                continue
            if len(last_date) > 0:
                sep_date.insert(0, last_date[j])
                sep_data.insert(0, last_data[j])
                j+=1
            day = str(sep_year[i-1]) + "-" + str(sep_month[i-1]) + "-" + str(sep_day[i-1])
            daily_data = pd.DataFrame({'DATETIME': sep_date[:-1],
                                       'cpu0': sep_data[:-1]})
            df_daily = daily_data.to_csv("./separated_cpu/daily/" + day + ".csv")
            last_date.append(sep_date[-1])
            last_data.append(sep_data[-1])
            sep_data.clear()
            sep_date.clear()
            sep_year.clear()
            sep_month.clear()
            sep_day.clear()
            i=0


for monthly_file in monthlypath:
    name, ext = os.path.splitext(os.path.basename(monthly_file))
    new_df = pd.read_csv(monthly_file, index_col=0)
    new_df = new_df.reset_index()
    new_df['DATETIME'] = pd.to_datetime(new_df['DATETIME'], format= '%Y-%m-%d %H:%M')
    new_df['cpu0'] = new_df['cpu0'].values.astype(float)
    data = new_df.groupby('DATETIME')['cpu0'].sum().reset_index()
    data = data.set_index(['DATETIME'])

    data.plot()
    plt.savefig("./separated_cpu/monthly/row/row_" + name + ".png")
    plt.close()

    #トレンド成分抽出
    res = sm.tsa.seasonal_decompose(data.values, freq=1440)
    res.plot()
    plt.savefig("./separated_cpu/monthly/res/res_" + name + ".png")
    plt.close()

    trend = res.trend
    trend = pd.DataFrame({'trend': trend, 'DATETIME':data.index})
    trend['DATETIME'] = pd.to_datetime(trend['DATETIME'], format='%Y-%m-%d %H:%M')
    trend_csv = trend.to_csv("./separated_cpu/monthly/trend/trend_" + name + ".csv")
    trend = trend.set_index(['DATETIME'])
    trend.plot()
    plt.savefig("./separated_cpu/monthly/trend/trend_" + name + ".png")
    plt.close()

#1dayベースでの前処理
for daily_file in dailypath:
    name, ext = os.path.splitext(os.path.basename(daily_file))
    new_df_d = pd.read_csv(daily_file, index_col=0)
    new_df_d = new_df_d.reset_index()
    new_df_d['DATETIME'] = pd.to_datetime(new_df_d['DATETIME'], format= '%Y-%m-%d %H:%M')
    new_df_d['cpu0'] = new_df_d['cpu0'].values.astype(float)
    data = new_df_d.groupby('DATETIME')['cpu0'].sum().reset_index()
    data = data.set_index(['DATETIME'])

    data.plot()
    plt.savefig("./separated_cpu/daily/row/row_" + name + ".png")
    plt.close()

    #トレンド成分抽出
    res = sm.tsa.seasonal_decompose(data.values, freq=60)
    res.plot()
    plt.savefig("./separated_cpu/daily/res/res_" + name + ".png")
    plt.close()

    trend = res.trend
    trend = pd.DataFrame({'trend': trend, 'DATETIME':data.index})
    trend['DATETIME'] = pd.to_datetime(trend['DATETIME'], format='%Y-%m-%d %H:%M')
    trend_csv = trend.to_csv("./separated_cpu/daily/trend/trend_" + name + ".csv")
    trend = trend.set_index(['DATETIME'])
    trend.plot()
    plt.savefig("./separated_cpu/daily/trend/trend_" + name + ".png")
    plt.close()

