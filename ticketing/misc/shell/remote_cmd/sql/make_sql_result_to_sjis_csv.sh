#!/bin/bash
set -eu
export LC_CTYPE=C
export LANG=C

cat << EOS
#---------------------------
# 処理の概要
#---------------------------
SQLの実行結果をShift JIS形式のCSVファイルに変換し、Excelで開けるようにします。
第一引数にカレントディレクトリ内にある変換したいファイル名を選択してください。

コマンド実行方法) bash <本スクリプトの親ディレクトリ>/make_sql_result_to_sjis_csv.sh <Shift JISにしたいファイル>

EOS

# シェル共通設定・関数の読み込み
CWD=$(cd $(dirname $0) && pwd)
[ -f ${CWD}/../../common/config.sh ] && . ${CWD}/../../common/config.sh
[ -f ${CWD}/../../common/function.sh ] && . ${CWD}/../../common/function.sh

file=${1}
file_name=${file%.*}

echo "変換後のファイル名は${txtyellow}sjis_${file_name}.csv${txtreset}になります。"

cat ${file} | tr '\t' ',' > ./.tmp.txt
nkf -sLw ./.tmp.txt > ./sjis_${file_name}.csv
rm ./.tmp.txt

cat << EOS
---------------------------
処理が完了しました。
---------------------------
EOS

exit 0