#!/bin/bash
set -eu

cat << EOS
#---------------------------
# 処理の概要
#---------------------------

DBにファミポート連携用のデータを登録

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
. "${CWD}/config.sh"
. "${CWD}/function.sh"

### 設定内容の出力
cat << EOS
CODE: ${CODE}
ORG_NAME: ${ORG_NAME}
WHO_AM_I: ${WHO_AM_I}
STANDBY_DB: ${STANDBY_DB}
STANDBY_DB_FMP: ${STANDBY_DB_FMP}
MASTER_DB: ${MASTER_DB}
STANDBY_PORT: ${STANDBY_PORT}
MASTER_PORT: ${MASTER_PORT}
PROD_SERVER: ${PROD_SERVER}
STG_SERVER: ${STG_SERVER}
FP_TENANT_CODE: ${FP_TENANT_CODE}
EOS

read -p "上記のDBにファミポート連携用のデータを登録します。続けるにはエンターキーを、中止するには「CTRL＋C」を押してください"

cat << EOS
#---------------------------
# 実行環境選択
#---------------------------
EOS

TARGET_ENV=$(ask "データ登録対象の環境を選択してください 。[ prod（本番）, stg（ステージング） ]> ")
case "${TARGET_ENV}" in
prod)
    echo "${txtred}本番DBにデータを登録します。${txtreset}"
    TARGET_SERVER=${PROD_SERVER}
    ;;
stg)
    echo "ステージングDBにデータを登録します"
    TARGET_SERVER=${STG_SERVER}
    ;;
*)
    echo "選択が不適切です。"
    exit 1
    ;;
esac

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
# ORG_IDの確認
#---------------------------
EOS

connect="mysql -u ticketing_ro -pticketing -h ${STANDBY_DB} -P ${STANDBY_PORT} -D ticketing"
sql=$(cat << EOS
SELECT * FROM Organization WHERE code = "${CODE}"\G
EOS
)
echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}
echo "${txtyellow}注意：この段階で複数の組織レコードの表示や、組織レコード自体が表示されない場合はORG追加手順の「管理画面ADMIN権限ユーザで実施」を見直してください。${txtreset}"

ORG_ID=$(ask "「id: xxx」を入力してください。")
echo "組織ID：${ORG_ID}の設定を行います。"

cat << EOS
#---------------------------
# 下記のDB.テーブルにデータが未作成であることを確認します。
#
# - ticketing.FamiPortTenant
# - ticketing.FamiPortTicketTemplate
# - famiport.FamiPortClient
#
#---------------------------
EOS

connect="mysql -u ticketing_ro -pticketing -h ${STANDBY_DB} -P ${STANDBY_PORT} -D ticketing"
sql=$(cat << EOS
SELECT * FROM FamiPortTenant WHERE organization_id = ${ORG_ID}\G
SELECT * FROM FamiPortTicketTemplate WHERE organization_id = ${ORG_ID}\G
EOS
)
cat << EOS
---------------------------
${STANDBY_DB}で以下のSQLを実行します。

${sql}

---------------------------
EOS
echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}
confirm "DB:ticketingにデータが未作成であることが確認できましたか？レコードが表示されなければ未作成です。(y)"

connect="mysql -u famiport_ro -pfamiport -h ${STANDBY_DB_FMP} -P ${STANDBY_PORT} -D famiport"
sql=$(cat << EOS
SELECT * FROM FamiPortClient WHERE code = "${FP_TENANT_CODE}";
EOS
)
cat << EOS
---------------------------
${STANDBY_DB_FMP}で以下のSQLを実行します。

${sql}

---------------------------
EOS
echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}
confirm "DB:famiportにデータが未作成であることが確認できましたか？レコードが表示されなければ未作成です。(y)"

cat << EOS
#---------------------------
#
# データ登録の実施
#
#---------------------------
EOS

connect="mysql -u ticketing -pticketing -h ${MASTER_DB} -P ${MASTER_PORT} -D ticketing"
sql=$(cat << EOS
BEGIN;

INSERT INTO FamiPortTicketTemplate (template_code,logically_subticket,mappings,organization_id,name)
SELECT template_code, logically_subticket, mappings, ${ORG_ID}, REPLACE(name, "BC", "${CODE}") FROM FamiPortTicketTemplate WHERE organization_id = 56;

INSERT INTO FamiPortTenant (organization_id, name, code, created_at, updated_at)
SELECT id, name, "${FP_TENANT_CODE}", now(), now()  FROM Organization WHERE id = ${ORG_ID};

COMMIT;
EOS
)
cat << EOS
---------------------------
${MASTER_DB}のDB:ticketingに次のSQLを実行します。

${sql}

---------------------------
EOS

select=$(ask "${txtyellow}よろしいですか？${txtreset}[ y（実行）, s（スキップ） ]> ")
case "${select}" in
y)
    echo "実行します。"
    echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}
    ;;
s)
    echo "スキップします。"
    ;;
*)
    echo "選択が不適切です。"
    exit 1
    ;;
esac

org_name_modify=$(ask "${txtred}FamiPortClient.nameは全角25文字以下で登録される必要があります（現在値：${ORG_NAME}）。${txtreset}[ 文字入力（修正実施）, エンターキー（スキップ） ]> ")
if [ -n "${org_name_modify}" ]; then
    org_name_zen=${org_name_modify}
else
    org_name_zen=${ORG_NAME}
fi

connect="mysql -u famiport -pfamiport -h ${MASTER_DB_FMP} -P ${MASTER_PORT} -D famiport"
sql=$(cat << EOS
BEGIN;

INSERT INTO FamiPortClient (famiport_playguide_id, code, name, prefix, auth_number_required, created_at, updated_at)
VALUES (1, "${FP_TENANT_CODE}", "${org_name_zen}", RIGHT("${FP_TENANT_CODE}", 3), 0, now(), now());

COMMIT;
EOS
)
cat << EOS
---------------------------
${MASTER_DB_FMP}のDB:famiportに次のSQLを実行します。

${sql}

---------------------------
EOS

select=$(ask "${txtyellow}よろしいですか？${txtreset}[ y（実行）, s（スキップ） ]> ")
case "${select}" in
y)
    echo "実行します。"
    echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}
    ;;
s)
    echo "スキップします。"
    ;;
*)
    echo "選択が不適切です。"
    exit 1
    ;;
esac

cat << EOS
#---------------------------
# 登録結果確認
#
# - ticketing.FamiPortTenant
# - ticketing.FamiPortTicketTemplate
# - famiport.FamiPortClient
#
#---------------------------
EOS

connect="mysql -u ticketing_ro -pticketing -h ${STANDBY_DB} -P ${STANDBY_PORT} -D ticketing"
sql=$(cat << EOS
SELECT * FROM FamiPortTenant WHERE organization_id = ${ORG_ID}; ;\G
SELECT * FROM FamiPortTicketTemplate WHERE organization_id = ${ORG_ID}\G
EOS
)
echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}
connect="mysql -u famiport_ro -pfamiport -h ${STANDBY_DB_FMP} -P ${STANDBY_PORT} -D famiport"
sql=$(cat << EOS
SELECT * FROM FamiPortClient WHERE code = "${FP_TENANT_CODE}";
EOS
)
echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_SERVER}
confirm "登録内容に問題がないことを確認してください(y)"

cat << EOS
---------------------------
処理が完了しました。
---------------------------
EOS

exit 0
