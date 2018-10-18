#!/bin/bash
files="*.rrd"
startstr='<database>'
endstr='<\/database>'
tagstr='<cf>'
unitstr='<pdp_per_row>'

#各rrdファイルに対してループ処理
for file in $files; do
  #path情報を除去
  faname_ext="${file##*/}"
  #拡張子を除去
  fname="${faname_ext%.*}"
  echo "===${fname}の処理を開始します==="
  ##rrdファイルを展開するツールをインストール済み
  ##その展開コマンドを使ってファイル操作（dumpは展開の意味)
  #rrdファイル中には複数のブロックがある。各開始・終了位置をタグで指定する
  s_strt_db=`rrdtool dump $file | less | sed -n "/${startstr}/="`
  s_end_db=`rrdtool dump $file | less | sed -n "/${endstr}/="`
  s_type_para=`rrdtool dump $file | less | sed -n "/${tagstr}/="`
  s_type_unit=`rrdtool dump $file | less | sed -n "/${unitstr}/="`

  #各開始・終了位置を配列に格納（後述のループ処理のため）
  a_strt_db=($s_strt_db)
  a_end_db=($s_end_db)
  a_type_para=($s_type_para)
  a_type_unit=($s_type_unit)

  #抽出した配列に対して処理
  #データ数が同じであることを確認させる（ループで使う範囲がどちらか一方になるため）
  if [ ${#a_strt_db[@]} -eq ${#a_end_db[@]} ]; then
    size_array=${#a_strt_db[@]}
    #各タグに対してループ開始
    for ((num=0; num < $size_array; num++)); do
      echo "===`expr ${num} + 1 `/${size_array}番目のデータを処理中===="
      #デバッグ用：処理行数を表示するための行番号を指定。expr使わないと計算できない
      strt=`expr ${a_strt_db[$num]} + 1`
      eend=`expr ${a_end_db[$num]} - 1`
      #averageなのかmaxなのかをタグを探しだして抽出する
      type_para=`rrdtool dump $file | less | sed -n "${a_type_para[$num]}p" | sed -e 's/<[^>]*>//g'`
      #分表示になっているので秒表示にする
      type_unit=`rrdtool dump $file | less | sed -n "${a_type_unit[$num]}p" | sed -e 's/<[^>]*>//g'`
      para=`echo ${type_para,,}`
      sec="`expr ${type_unit} \* 60`sec"
      echo "===データ範囲は${strt}～${eend}まで==="
      filename="${fname}_${para}_${sec}"
      txtfile="${filename}.txt"
      csvfile="${filename}.csv"

      #上記で作成したテキストファイルの存在チェックをしてその中にrrdファイルの中身を書き込んであげる
      if [ ! -e $txtfile ]; then
        echo `rrdtool dump $file | less | sed -n "${strt},${eend}p" > ${txtfile}`
      fi

      #csvファイルの存在チェック。重複防止のため
      if [ -e $csvfile ]; then
        rm -rf $csvfile
      fi
      #次のカラム名でCSVファイル作成
      echo "DATETIME,INPUT,OUTPUT" > ${csvfile}
      #行数のみを取り出す
      linesize=`cat ${txtfile} | wc -l`
       #データを整形しcsvで出力
       cnt=1
      #書き込んだテキストファイルをから"!"をさよならして各行に対してループ
      #一行ごとに処理するためめっちゃ時間かかる
      less ${txtfile} | sed -e 's/\!//' | while read line
      do
        #ディレクティブを削除
        s_dstrt=`echo $line | grep -o '<v[^>]*>[^<]*<\/v>' | sed -e 's/<v>\(.*\)<\\/v>/\1/'`
        #上記を配列に格納
        a_dstrt=($s_dstrt)
        #一部の場所でスペース区切りがあるのでカンマ区切りに変換する
        ddate=`echo ${line:4:19}`
        datetime=`date -d "${ddate}" "+%Y/%m/%d %H:%M"`
        data1=${a_dstrt[0]}
        data2=${a_dstrt[1]}
        adate=$datetime
        adata1=($data1)
        adata2=($data2)
        alldata="${adate},${adata1},${adata2}"
        echo $alldata >> ${csvfile}
        convertrate=`echo "scale=3; ${cnt} / ${linesize} * 100" | bc`
        echo "$fname:${adate}"
        cnt=$(( cnt + 1 ))
      done
      if [ $convertrate -eq 100% ]; then
        echo "${csvfile}を出力しました"
      fi
      #csv作ったらtxtファイルを削除する
      if [ -e $csvfile ]; then
        rm -rf $txtfile
      fi
    done
  else
    exit 0
  fi
done
