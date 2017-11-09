#!/bin/bash
set -eu

cat << EOS
#---------------------------
# 処理の概要
#---------------------------

FamiportへFTPで画像を送信します。

EOS

cat << EOS
#---------------------------
# 設定値
#---------------------------
EOS

# シェル共通設定・関数の読み込み
CWD=$(cd $(dirname $0) && pwd)
[ -f ${CWD}/../common/config.sh ] && . ${CWD}/../common/config.sh
[ -f ${CWD}/../common/function.sh ] && . ${CWD}/../common/function.sh

# ORG追加独自設定・関数の読み込み
relative_source config.sh
relative_source function.sh

### 設定内容の出力
cat << EOS
CODE: ${CODE}
WHO_AM_I: ${WHO_AM_I}
FP_TENANT_CODE: ${FP_TENANT_CODE}
FP_IMG_DIR_PATH: ${FP_IMG_DIR_PATH}
SLAVE_DB: ${SLAVE_DB}
MASTER_DB: ${MASTER_DB}
PROD_SERVER: ${PROD_SERVER}
STG_SERVER: ${STG_SERVER}
FP_IMG_PROD_SERVER: ${FP_IMG_PROD_SERVER}
FP_IMG_STG_SERVER: ${FP_IMG_STG_SERVER}
EOS

read -p "続けるにはエンターキーを、中止するには「CTRL＋C」を押してください"

cat << EOS
#---------------------------
# 実行環境選択
#---------------------------
EOS

TARGET_ENV=$(ask "データ登録対象の環境を選択してください 。[ prod（本番）, stg（ステージング） ]> ")
case "${TARGET_ENV}" in
prod)
    echo "${txtred}本番環境を対象に処理を進めます。${txtreset}"
    TARGET_SERVER=${PROD_SERVER}
    FP_IMG_SERVER=${FP_IMG_PROD_SERVER}

    declare -a CURL_OPTIONS=()
    PRE_IFS=$IFS
    IFS=$'\n'
    for opt in ${CURL_PROD_OPTIONS[@]}; do
        CURL_OPTIONS+=(${opt})
    done
    IFS=${PRE_IFS}
    ;;
stg)
    echo "ステージング環境を対象に処理を進めます。"
    TARGET_SERVER=${STG_SERVER}
    FP_IMG_SERVER=${FP_IMG_STG_SERVER}

    declare -a CURL_OPTIONS=()
    PRE_IFS=$IFS
    IFS=$'\n'
    for opt in ${CURL_STG_OPTIONS[@]}; do
        CURL_OPTIONS+=(${opt})
    done
    IFS=${PRE_IFS}
    ;;
*)
    echo "選択が不適切です。"
    exit 1
    ;;
esac

cat << EOS
#---------------------------
即時反映を実行しますか？

"""
夜間バッチによる取り込みは1日に1回で、EVENT_IMG.zipを1日に複数回送信すると先に送ったものが取り込み時に上書きされてしまう。
緊急で即時反映したい場合は、"EVENT_DIFF_IMG.zip"というファイル名で送信することにより、５～１０分間隔で実行されているバッチにて取り込まれる。
"EVENT_IMG.zip"が全てを送りなおす洗い替え方式であるのに対して"EVENT_DIFF_IMG.zip"は差分のみを送る差分方式。
"EVENT_DIFF_IMG.zip"を連続して送信する場合は上書き防止のため10分以上の間隔を空けてから送信する必要がある。
即時反映の場合は送信フラグ名を"EVENT_DIFF_IMG_FLG.txt"にする。
"""

引用:「興行資材反映手順」
https://redmine.ticketstar.jp/projects/altair/wiki/Fami%E3%83%9D%E3%83%BC%E3%83%88%E9%80%A3%E6%90%BA#%E8%88%88%E8%A1%8C%E8%B3%87%E6%9D%90%E5%8F%8D%E6%98%A0%E6%89%8B%E9%A0%86
#---------------------------
EOS

EFFECT_IMMEDIATELY=$(ask "[y(即時反映する) / その他のキー(通常手順)]> ")
case "${EFFECT_IMMEDIATELY}" in
y)
    FLG_FILE="EVENT_DIFF_IMG_FLG.txt"
    ZIP_FILE="EVENT_DIFF_IMG.zip"
    ;;
*)
    FLG_FILE="EVENT_IMG_FLG.txt"
    ZIP_FILE="EVENT_IMG.zip"
    ;;
esac

cat << EOS
#---------------------------
# リモートホスト(${TARGET_SERVER})との接続確認
#---------------------------
EOS

connected=$(echo "hostname" | remote_execution ${WHO_AM_I} ${TARGET_SERVER})
if [ $? -ne 0 ]; then
    echo "${txtred}リモートホスト「${TARGET_SERVER}」の接続に失敗しました。config.shを見直してください。${txtreset}"
    exit 1
fi
echo "${txtblue}正常に${connected}に接続しました。${txtreset}"


cat << EOS
#---------------------------
# FamiPortTenantのcodeを調べる
#---------------------------
EOS

connect="mysql -u ticketing_ro -pticketing -h ${SLAVE_DB} -P ${SLAVE_PORT} -D ticketing"
sql=$(cat << EOS
SELECT * FROM Organization WHERE code = "${CODE}"\G
EOS
)

echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}
echo "${txtyellow}注意：この段階で複数の組織レコードの表示や、組織レコード自体が表示されない場合はORG追加手順の「管理画面ADMIN権限ユーザで実施」を見直してください。${txtreset}"

ORG_ID=$(ask "「id: xxx」を入力してください。")
echo "組織ID：${ORG_ID}がticketing.FamiPortTenantに登録されていることを確認します。"

connect="mysql -u ticketing_ro -pticketing -h ${SLAVE_DB} -P ${SLAVE_PORT} -D ticketing"
sql=$(cat << EOS
SELECT id, organization_id, name, code FROM FamiPortTenant WHERE organization_id = ${ORG_ID};
EOS
)
echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}

confirm "「code」は${FP_TENANT_CODE}と一致していますか？(y)"


cat << EOS
#---------------------------
# 画像をまとめて、送信用のサーバーに配置する
#---------------------------
EOS

cd ${FP_IMG_DIR_PATH}

# 既存のzipファイルがあれば削除
test -e ${ZIP_FILE} && rm ${ZIP_FILE}
zip -r ${ZIP_FILE} *.jpg *.png

echo "生成されたzipファイルの内容に問題がないか確認してください。"
unzip -l ${ZIP_FILE}
confirm "${FP_IMG_SERVER}にSCP送信します。よろしいですか？(y)"

scp -o "ProxyCommand ssh ${WHO_AM_I}@gk1c.vpc.altr.jp nc %h %p" ${ZIP_FILE} ${WHO_AM_I}@${FP_IMG_SERVER}.vpc.altr:~/

cd -

cat << EOS
#---------------------------
#
# FTP送信 ${FP_IMG_SERVER}.vpc.altr
#
#---------------------------
EOS

echo "${FP_IMG_SERVER}にSCPでzipファイルがアップロードされたか確認します。"

echo "${txtyellow}${FP_IMG_SERVER}.vpc.altrでpwd:${txtreset} `echo "pwd" | remote_execution ${WHO_AM_I} "${FP_IMG_SERVER}.vpc.altr"`"
echo "${txtyellow}${FP_IMG_SERVER}.vpc.altrでls -la:${txtreset} `echo "ls -la" | remote_execution ${WHO_AM_I} "${FP_IMG_SERVER}.vpc.altr"`"
echo "${txtyellow}${FP_IMG_SERVER}.vpc.altrでunzip -l ${ZIP_FILE}:${txtreset} `echo "unzip -l ${ZIP_FILE}" | remote_execution ${WHO_AM_I} "${FP_IMG_SERVER}.vpc.altr"`"
confirm "FTP送信してよろしいですか？(y)"

PRE_IFS=$IFS
IFS=$'\n'

for opt in ${CURL_OPTIONS[@]}; do
    echo "${txtyellow}「${FP_IMG_SERVER}.vpc.altr」で「curl -T ${ZIP_FILE} -k ${opt}」を実行します。${txtreset}"
    echo "curl -T ${ZIP_FILE} -k ${opt}" | remote_execution ${WHO_AM_I} "${FP_IMG_SERVER}.vpc.altr"
done

echo "${txtyellow}「${FP_IMG_SERVER}.vpc.altr」で「touch ${FLG_FILE}」を実行します。${txtreset}"
echo "touch ${FLG_FILE}" | remote_execution ${WHO_AM_I} "${FP_IMG_SERVER}.vpc.altr"
for opt in ${CURL_OPTIONS[@]}; do
    echo "${txtyellow}「${FP_IMG_SERVER}.vpc.altr」で「curl -T ${FLG_FILE} -k ${opt}」を実行します。${txtreset}"
    echo "curl -T ${FLG_FILE} -k ${opt}" | remote_execution ${WHO_AM_I} "${FP_IMG_SERVER}.vpc.altr"
done

echo "結果を確認します。"
for opt in ${CURL_OPTIONS[@]}; do
    echo "${txtyellow}「${FP_IMG_SERVER}.vpc.altr」で「curl -k ${opt}」を実行します。${txtreset}"
    echo "curl -k ${opt}" | remote_execution ${WHO_AM_I} "${FP_IMG_SERVER}.vpc.altr"
done
echo ${txtreset}

IFS=${PRE_IFS}

if [ "${FP_IMG_SERVER}" = "${FP_IMG_STG_SERVER}" ]; then
    cat << EOS
#---------------------------
 ${txtyellow}STG環境のFTP送信が完了しました。${txtreset}

 画像がとりこまれると、その旨メールが２通届くので確認してください。

 ===========================
  【FTPS受信】興行IMG：日次（Y系）
  【FTPS受信】興行IMG：日次（Z系）
 ===========================

 確認できたら本番用の画像を送ります。

#---------------------------
EOS
fi

if [ "${FP_IMG_SERVER}" = "${FP_IMG_PROD_SERVER}" ]; then
    cat << EOS
#---------------------------
 ${txtyellow}本番環境のFTP送信が完了しました。${txtreset}

 画像がとりこまれると、その旨メールが２通届くので確認してください。

 ===========================
  【FTPS受信】興行IMG：日次（X1系）
  【FTPS受信】興行IMG：日次（X2系）
 ===========================

 おつかれさまでした。

#---------------------------
EOS
fi

cat << EOS
---------------------------
処理が完了しました。
---------------------------
EOS

exit 0
