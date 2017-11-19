#!/bin/bash
set -eu

cat << EOS
#---------------------------
# 処理の概要
#---------------------------

ローカル環境からリモート環境にSQLを実施。
結果はローカル環境のカレントディレクトリに取得します。

※ STANDBY_DBにしか接続しないため、SELECT文のSQLのみ実行してください。

実行例:
bash <親ディレクトリまでのパス>/main.sh
→ 対話形式で処理が実行されます。SQL実行前に最終確認が表示されます。


EOS

cat << EOS
#---------------------------
# 設定値
#---------------------------
EOS

# シェル共通設定・関数の読み込み
CWD=$(cd $(dirname $0) && pwd)
[ -f ${CWD}/../../common/config.sh ] && . ${CWD}/../../common/config.sh
[ -f ${CWD}/../../common/function.sh ] && . ${CWD}/../../common/function.sh

# 独自設定・関数の読み込み
relative_source config.sh
relative_source function.sh

### 設定内容の出力
cat << EOS
WHO_AM_I: ${WHO_AM_I}
STG_SERVER: ${STG_SERVER}
PROD_SERVER: ${PROD_SERVER}
STANDBY_DB: ${STANDBY_DB}
MASTER_DB: ${MASTER_DB}
STANDBY_PORT: ${STANDBY_PORT}
MASTER_PORT: ${MASTER_PORT}
EOS

read -p "続けるにはエンターキーを、中止するには「CTRL＋C」を押してください"

cat << EOS
#---------------------------
# 実行環境選択
#---------------------------
EOS

echo "SQLリスト: "
for choice in $( ls ${CWD}/script/*.sql ); do
  echo "${choice}"
done

sql_file=$(ask "実行するSQLファイル名を入力してください。>")
target_sql_path="${CWD}/script/${sql_file}"
ls ${target_sql_path}
if [ $? -ne 0 ]; then
    echo echo "${txtred}選択したファイルが存在しません。${txtreset}"
    exit 1
fi

select=$(ask "SQLの実行環境を選択してください 。[ prod（本番）, stg（ステージング） ]>")
case "${select}" in
prod)
    echo "${txtred}本番DBでSQLを実行します。${txtreset}"
    TARGET_SERVER=${PROD_SERVER}
    ;;
stg)
    echo "ステージングDBでSQLを実行します。"
    TARGET_SERVER=${STG_SERVER}
    ;;
*)
    echo "選択が不適切です。"
    exit 1
    ;;
esac

database=$(ask "データベースを選択してください。[ ticketing, famiport, altaircms, extauth ]>")
echo "データベース: ${database}が選択されました。"

cat << EOS
#---------------------------
# リモートホストとの接続確認
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
# SQL実行
#---------------------------
EOS

connect="mysql -u ${database}_ro -p${database} -h ${STANDBY_DB} -P ${STANDBY_PORT} -D ${database}"
sql=$(cat ${target_sql_path})
cat << EOS

${txtyellow}MYSQL接続先:${txtreset}
${connect}

${txtyellow}実行SQL:${txtreset}
${sql}

---------------------------
EOS
confirm "よろしいですか？(y)"

echo "SCPで${TARGET_SERVER}に「.tmp_${sql_file}」を一時的に作成します。"
scp -o "ProxyCommand ssh ${WHO_AM_I}@gk1c.vpc.altr.jp nc %h %p" "${target_sql_path}" ${WHO_AM_I}@${TARGET_SERVER}:~/.tmp_${sql_file}

echo "${connect} < ~/.tmp_${sql_file}" | remote_execution ${WHO_AM_I} ${TARGET_SERVER} > ./${sql_file}_res.txt
echo "SQLの実行が完了。"
echo "「.tmp_${sql_file}」を削除します。"
echo "rm -f ~/.tmp_${sql_file}" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}

cat << EOS
---------------------------
${txtyellow}実行結果:${txtreset}

$(cat ./${sql_file}_res.txt)

EOS

cat << EOS

処理が完了しました。

実行結果は${txtyellow}「less ${sql_file}_res.txt」${txtreset}に出力してあります。
---------------------------
EOS

select=$(ask "文字コードをShift-JISに変換したファイルの作成も行いますか？(y)")
case "${select}" in
y)
    bash "${CWD}/make_sql_result_to_sjis_csv.sh" "${sql_file}_res.txt"
    ;;
*)
    echo "終了します。"
    exit 0
    ;;
esac
