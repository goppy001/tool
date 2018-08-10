#!/bin/bash
files="/home/hoge/*.rrd"
startstr='<database>'
endstr='<\/database>'
tagstr='<cf>'
unitstr='<pdp_per_row>'

#各rrdファイルに対してループ処理
for file in $files; do
  faname_ext="${file##*/}"
  fname="${faname_ext%.*}"
  echo "===${fname}の処理を開始します==="
  s_strt_db=`rrdtool dump $file | less | sed -n "/${startstr}/="`
  s_end_db=`rrdtool dump $file | less | sed -n "/${endstr}/="`
  s_type_para=`rrdtool dump $file | less | sed -n "/${tagstr}/="`
  s_type_unit=`rrdtool dump $file | less | sed -n "/${unitstr}/="`

  a_strt_db=($s_strt_db)
  a_end_db=($s_end_db)
  a_type_para=($s_type_para)
  a_type_unit=($s_type_unit)
  
  #抽出した配列に対して処理
  if [ ${#a_strt_db[@]} = ${#a_end_db[@]} ]; then
    size_array=${#a_strt_db[@]}
    for ((num=0; num < $size_array; num++)); do
      echo "===`expr ${num} + 1 `/${size_array}番目のデータを処理中===="
      strt=`expr ${a_strt_db[$num]} + 1`
      eend=`expr ${a_end_db[$num]} - 1`
      type_para=`rrdtool dump $file | less | sed -n "${a_type_para[$num]}p" | sed -e 's/<[^>]*>//g'` 
      type_unit=`rrdtool dump $file | less | sed -n "${a_type_unit[$num]}p" | sed -e 's/<[^>]*>//g'`
      para=`echo ${type_para,,}`
      sec="`expr ${type_unit} \* 60`sec"
      echo "===データ範囲は${strt}～${eend}まで==="
      filename="${fname}_${para}_${sec}"
      txtfile="${filename}.txt"
      csvfile="${filename}.csv"
      echo `rrdtool dump $file | less | sed -n "${strt},${eend}p" > ${txtfile}`

      #ファイル存在チェック
      if [ -e $csvfile ]; then
        rm -rf $csvfile
      fi
      #次のヘッダでCSVファイル作成
      echo "DATE,TIME,INPUT,OUTPUT" > ${csvfile}
      linesize=`cat ${txtfile} | wc -l`
       #データを整形しcsvで出力
       cnt=1
      less ${txtfile} | sed -e 's/\!//' | while read line
      do
        s_dstrt=`echo $line | grep -o '<v[^>]*>[^<]*<\/v>' | sed -e 's/<v>\(.*\)<\\/v>/\1/'`
        a_dstrt=($s_dstrt)
        ddate=`echo ${line:4:19} | tr ' ' ','`
        data1=${a_dstrt[0]}
        data2=${a_dstrt[1]}
        adate=($ddate)
        adata1=($data1)
        adata2=($data2)
        alldata="${adate},${adata1},${adata2}"
        echo $alldata >> ${csvfile}
        convertrate="`expr ${cnt} / ${linesize} \* 100`%"
        echo "maxline:${linesize} now:${cnt} rate:${convertrate}"
        cnt=$(( cnt + 1 ))
      done
      if [ $convertrate = 100 ]; then
        echo "${csvfile}を出力しました"
      fi
    done
  else
    exit 0
  fi
done
