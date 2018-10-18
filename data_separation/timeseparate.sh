#!/bin/bash

#例えば2種類の時刻データがある。とする
#データAは1分間平均で値を取得、データBはリアルタイムでの取得
#データ分析などでデータBの時刻をデータAで近似したい。
#データBの時刻を秒の方から削除していき一番近いデータAの時刻に変換するツール
#なお、データAの時刻フォーマットは+%Y/%m/%d %H:%M表記とする。
#データBの時刻はこのスクリプトで変換する


#定数など
listservice='MEMORY'
targetservice='memory'
aleartfile="mail_list_*${listservice}*.csv"
targetfile="*${targetservice}*joined.csv"

outputfile="targetdate_list_${targetservice}.csv"
echo "DATETIME,MAIL_ID,SERVICE" > $outputfile

IFS=$'\n'
#アラートメールリストを一行ずつ解読
echo "アラートメールを一行ずつ見ます"
less ${aleartfile} | sed -e '1d' | while read line
do
  nowtime=`echo $line | cut -f 1 -d "," | sed -e "s/.\{2\}$/00/"`
  str_len=`echo -n $nowtime | wc -m`
  #アラートメールの時刻をターゲットから検索
  now=$nowtime
  for ((i=0; i < $str_len; i++)); do
    searchtext=`less ${targetfile} | sed -e '1d' | cut -f 2 -d "," | grep -c "$now"`
    if [ $searchtext -ge 1 ]; then
      array_search_result=(`less ${targetfile} | sed -e '1d' | cut -f 2 -d "," | grep "$now"`)
      echo "配列中身：${array_search_result[@]}"
      break
    elif [ $searchtext -eq 0 ]; then
      now=`echo ${now::-1}`
      echo "現在時刻:${now}"
    fi
  done
  #抽出した時刻候補の中からターゲット時刻より大きく、かつ差が最小の時刻を抽出する
  size_array=${#array_search_result[@]}
  echo "配列数:$size_array"
  s_nowtime=`date -d "${nowtime}" "+%s"`
  echo $s_nowtime
  array_s_date=()
  a_s_date=()
  #時刻をunixitimeに変換し計算できるようにする
  for ((num=0; num < $size_array; num++)); do
    s_date=`date -d "${array_search_result[$num]}" "+%s"`
    a_s_date+=($s_date)
    diff=`expr $s_nowtime - $s_date`
    array_s_date+=($diff)
  done
  echo "シリアル配列中身:${array_s_date[@]}"
  
  #シリアルが負がある場合、負の絶対値を使う、無い場合は正を使うための処理
  abs_array_minus=()
  abs_array_plus=()
  for j in ${array_s_date[@]}; do
    if [ $j -lt 0 ]; then
      echo "負のシリアル値：${j}"
      abs_array_minus+=(`perl -le "print abs(${j})"`)
    elif [ $j -ge 0 ]; then
      echo "正のシリアル値:${j}"
      abs_array_plus+=($j)
    fi
  done

  abs_array=()
  if [ ${#abs_array_minus[@]} -eq 0 ]; then
    for k in ${abs_array_plus[@]}; do
      abs_array+=($k)
    done
    value=`echo ${abs_array[@]} | sort -n | head -n 1`
    value=`echo ${abs_array[@]:1}`
  else
    for k in ${abs_array_minus[@]}; do
      abs_array+=($k)
    done
    value=`echo ${abs_array[@]} | sort -n | head -n 1`
    value=`expr \( -1 \) \* $value`
  fi

  #シリアル値を元の日付データに戻す
  echo ${a_s_date[@]}
  for ((cnt=0; cnt < ${#array_s_date[@]}; cnt++)); do
    if [ ${array_s_date[$cnt]} -eq $value ]; then
      s_time=${a_s_date[$cnt]}
      echo $s_time
      break
    fi
  done
  conv_time=`date -d "@${s_time}" "+%Y/%m/%d %H:%M:%S"`
  echo $conv_time
  mail_id=`echo $line | cut -f 2 -d ","`
  service_name=`echo $line | cut -f 3 -d ","`
  echo "$conv_time,$mail_id,$service_name" >> $outputfile
done
