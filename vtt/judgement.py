
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import glob
import re
import shutil
from datetime import datetime as dt
from vtt import basic, extract, statistics, threshold, vtt


def find(arg_file_path):
    for root, dirs, csvs in os.walk(arg_file_path):
        yield root
        for csv in csvs:
            yield os.path.join(root, csv)


TARGET_WORD = 'trend_cpu_'
target_files = glob.glob(TARGET_WORD + "*.csv")
list = []

#計算結果用ディレクトリ作成
work_dir = "./vtt"
basic.check_dir(work_dir)
#ログディレクトリ
result_log_path = work_dir + "/result_log"
basic.check_dir(result_log_path)
#計算用ファイルのディレクトリ存在チェック・作成
calc_dir = work_dir + "/data"
basic.check_dir(calc_dir)
#学習データディレクトリ
learn_dir = work_dir + "/learn"
basic.check_dir(learn_dir)
#履歴ディレクトリ
history = work_dir + "/history"
basic.check_dir(history)

#対象外ディレクトリリスト
exception_list = [work_dir, result_log_path, calc_dir, learn_dir, history, history + "/png", history + "/csv"]

#学習ファイル定義
learn_name = "default_learn.csv"
learn_file = work_dir + "/" + learn_name
#初期学習ファイルの移動
if os.path.isfile(learn_file):
    pass
else:
    shutil.move(learn_name, work_dir)


#計算用ファイルのコピペ
###ここから###
target_dir = "./"
target_list = []
size_list = []
for csvfile in find(target_dir):
    name, ext = os.path.splitext(os.path.basename(csvfile))
    if ext == ".csv":
        df = pd.read_csv(str(csvfile), index_col=0)
        df_data = df.iloc[:, 1].values
        size_list.append(df_data.shape[0])
        target_list.append(csvfile)

#各CSVをひとつのCSVにまとめて出力する
tmp_list = []
dir_list = []
for i, file in enumerate(target_list):
    dire = os.path.dirname(file)
    if size_list[i] < max(size_list):
        continue
    if any(dire == arg for arg in exception_list):
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

target_files = ["./" + re_dir_list[i] + "/trend_cpu_" +
                str(tf) + ".csv" for i, tf in enumerate(re_list)]

index_list = []
#リストフィルタ
for i, file in enumerate(target_files):
    df_learn = pd.read_csv(work_dir + "/default_learn.csv", index_col=0)
    df_col_name = df_learn.columns[1]
    file_name, _ = os.path.splitext(os.path.basename(file))
    file_name = file_name.replace("trend_cpu_", "")
    file_name = pd.to_datetime(file_name, format='%Y-%m-%d')
    rename_pattern = "(.*) (.*)"
    d = re.search(str(rename_pattern), str(file_name))
    file_name = d.group(1)
    if str(file_name) == str(df_col_name):
        index_list.append(i)
        break
#ファイルコピー
index = index_list[0]
target_files = target_files[index + 1:]
for file in target_files:
    shutil.copy(file, calc_dir)
###ここまで###

re_target_files = glob.glob(calc_dir + "/*")

#比較される側のファイル名を抽出
for tf in re_target_files:
    name, _ = os.path.splitext(os.path.basename(tf))
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
target_files = [calc_dir + "/" + TARGET_WORD + str(tf) + ".csv" for tf in re_list]

####################################
### メイン処理 ###
####################################

d = 90          #何日分のデータを使って閾値を計算するか
n = 2           #μ±nσのn データが正規分布に従う場合n=2 => 95%, n=3 => 99%に含まれないデータは異常とされる
METRIC = 'wma'  #平均値を求める方法
SERVICE = 'cpu' #対象となるサービス名
LIMIT_TIMES = 3 #しきい値を連続何回超えたら「しきい値超え」とみなすかの限界値(x >= LIMIT_TIMES で発動)
prev_data = []

log_threshold = open("threshold_log.txt", 'a')

#各ファイルに対して閾値判定を実施
for i, file in enumerate(target_files):
    df_target = pd.read_csv(file, index_col=0)
    df_time   = extract.time(df_target)
    name = extract.ext_name(file, strg=TARGET_WORD)
    print(name)
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
    if i > 0:
        df_data  = pd.concat([prev_data, df_data], ignore_index=True).dropna()
        df_data  = df_data.values
        prev_data = df_target.iloc[:, 1].iloc[-num_na:]
        prev_data.reset_index()
        df_data = pd.DataFrame(df_data)
        
    up_th = up_th.values
    lw_th = lw_th.values
    df_data = df_data.values
    diff_up = df_data - up_th
    diff_lw = df_data - lw_th

    log = open(result_log_path + "/result_log_" + name + ".txt", 'a')
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

    vtt.vtt(n, d, learn_file, file, df_data, work_dir, target_word=TARGET_WORD, metric=METRIC, service=SERVICE)
    #データがいずれかの時刻で一つでも閾値を超えていた場合
    if any(arg == True for arg in bool_up) or any(arg == True for arg in bool_lw):
        pass
    #閾値が超えていなければ閾値を更新するのでその処理を記述
    else:
        #learn_fileをここで更新することで次回閾値は学習結果を使うことになる
 
        new_learn_file = learn_dir + "/" + learn_file
        if basic.check_dir(learn_dir):
            learn_file = threshold.update(d, file, df_data, new_learn_file, target_word=TARGET_WORD)
        else:
            learn_file = threshold.update(d, file, df_data, learn_file, work_dir, target_word=TARGET_WORD)
        log_write = log_threshold.write(str(i) + ": " + str(name) + "でしきい値を変更しました。" + '\n')
log_threshold.close()
