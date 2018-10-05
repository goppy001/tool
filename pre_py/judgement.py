#!/home/hogehoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import glob
import re
from datetime import datetime as dt
from vtt import extract, statistics, threshold, vtt

TARGET_WORD = 'trend_cpu_'
learn_file = "default_learn.csv"
target_files = glob.glob(TARGET_WORD + "*.csv")
list = []

#比較される側のファイル名を抽出
for tf in target_files:
    name, _ = os.path.splitext(tf)
    name = name.replace(TARGET_WORD, "")
    rename = pd.to_datetime(name, format='%Y-%m-%d')
    rename_pattern = "(.*) (.*)"
    d = re.search(str(rename_pattern), str(rename))
    list.append(d.group(1))

#日付を降順にするためソート
list = sorted(list)
re_list = []
#上記ソートだけではだめなので文字型の日付をdatetime型に変換してリストに再代入
for file in list:
    name = pd.to_datetime(file, format='%Y-%m-%d')
    rename = '{d.year}-{d.month}-{d.day}'.format(d=name)
    re_list.append(rename)
target_files = [TARGET_WORD + str(tf) + ".csv" for tf in re_list]

####################################
### メイン処理 ###
####################################

#何日分のデータを使って閾値を計算するか
d = 90
"""
#μ±nσのn
#データが正規分布に従う場合n=2 => 95%, n=3 => 99%に含まれないデータは異常とされる
"""
n = 2
log_threshold = open("threshold_log.txt", 'a')
METRIC = 'wma'
SERVICE = 'cpu'
LIMIT_TIMES = 3
prev_data = []

#各ファイルに対して閾値判定を実施
for i, file in enumerate(target_files):
    df_target = pd.read_csv(file, index_col=0)
    df_time   = extract.time(df_target)
    name = extract.ext_name(file, strg=TARGET_WORD)
    df_data = df_target.iloc[:, 1]
    up_th, lw_th = threshold.threshold(n, d, learn_file, metric=METRIC, service=SERVICE)
    #前日データがある場合、それを現在ファイルに挿入する処理
    if i == 0:
        df_learn = pd.read_csv(learn_file, index_col=0)
        learn_data = df_learn.iloc[:,1]
        num_na = df_target.isnull().sum()
        num_na = num_na.iloc[1].astype(int)
        prev_data = learn_data.iloc[-num_na:]
        prev_data.reset_index()
        df_data  = pd.concat([prev_data, df_data], ignore_index=True).dropna()
        df_data  = df_data.values
        prev_data = df_target.iloc[:, 1].iloc[-num_na:]
        prev_data.reset_index()
        df_data = pd.DataFrame(df_data)
        print(df_data)
    if i > 0:
        df_data  = pd.concat([prev_data, df_data], ignore_index=True).dropna()
        df_data  = df_data.values
        prev_data = df_target.iloc[:, 1].iloc[-num_na:]
        prev_data.reset_index()
        df_data = pd.DataFrame(df_data)
        print(df_data)
        
    up_th = up_th.values
    lw_th = lw_th.values
    df_data = df_data.values
    diff_up = df_data - up_th
    diff_lw = df_data - lw_th

    log = open("result_log_" + name + ".txt", 'a')
    judge_up = []
    judge_lw = []
    bool_up  = []
    bool_lw  = []    
    for i in range(len(df_time)):
        """アラート出力を閾値超え連続n回で実施する
        閾値超えがn-1までなら閾値超えしていないものとみなして
        閾値更新もやる
        """
        if df_data[i] > up_th[i]:
            judge_up.append(True)
        else:
            judge_up.append(False)

        if df_data[i] < lw_th[i]:
            judge_lw.append(True)
        else:
            judge_lw.append(False)

        #要素数（ループ回数がn回かチェック）
        if len(judge_up) < LIMIT_TIMES and len(judge_lw) < LIMIT_TIMES:
            continue
        if len(judge_up) >= LIMIT_TIMES and len(judge_lw) >= LIMIT_TIMES:
            """
            特定回数で要素判別のため余りを出さないように条件分岐する。
            例えば3回連続で見たい場合は要素数が5とかだと意味がないので6になるまで待つ。
            その後でこの回数ごとに要素を再度リスト化するがほしいのは常に最新の情報＝リストの最後の情報
            であるためカウンタiをlimit_timesで割った商を使って常に
            最新の情報（要素）で閾値判定できるようにする
            例えばカウンタが6で3回連続を判定する場合、再リストは各要素に3個ずつ要素が入っているので2要素になる。
            ただし、判定したいのはindexでいう[1]の方なので商-1とすればどのようなnに対しても適用できる
            """
            if len(judge_up) % LIMIT_TIMES == 0:
                last_index = len(judge_up) % LIMIT_TIMES - 1
                up_bool_list = [judge_up[i:i + LIMIT_TIMES] for i in range(0, len(judge_up), LIMIT_TIMES)]
                lw_bool_list = [judge_lw[i:i + LIMIT_TIMES] for i in range(0, len(judge_lw), LIMIT_TIMES)]
                if len(up_bool_list) > 0:
                    if all(up_bool_list[last_index]):
                        message = str(i) + ": " + str(name) + " " + df_time.values[i] + "で上側しきい値を超えました" + '\n'
                        log_write = log.write(str(message))
                        bool_up.append(True)
                    else:
                        bool_up.append(False)
                if len(lw_bool_list) > 0:
                    if all(lw_bool_list[last_index]):           
                        message = str(i) +": " + str(name) + " " + df_time.values[i] + "で下側しきい値を超えました" + '\n'
                        log_write = log.write(str(message))
                        bool_lw.append(True)
                    else:
                        bool_lw.append(False)
            else:
                continue
    log.close()
    ##↑各行に対する処理を終了##
    vtt.vtt(n, d, learn_file, file, df_data, target_word=TARGET_WORD, metric=METRIC, service=SERVICE)
    #データがいずれかの時刻で一つでも閾値を超えていた場合
    if any([arg == True for arg in bool_up]) or any(arg == True for arg in bool_lw):
        pass
    #閾値が超えていなければ閾値を更新するのでその処理を記述
    else:
        #learn_fileをここで更新することで次回閾値は学習結果を使うことになる
        learn_file = threshold.update(d, file, df_data,learn_file, target_word=TARGET_WORD)
        log_write = log_threshold.write(str(i) + ": " + str(name) + "でしきい値を変更しました。" + '\n')
log_threshold.close()
