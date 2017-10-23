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

# 設定・関数の読み込み
CWD=$(cd $(dirname $0) && pwd)
[ -f ${CWD}/config.sh ] && . ${CWD}/config.sh
[ -f ${CWD}/function.sh ] && . ${CWD}/function.sh

### 設定内容の出力
cat << EOS
CODE: ${CODE}
ORG_NAME: ${ORG_NAME}
WHO_AM_I: ${WHO_AM_I}
SLAVE_DB_HOST: ${SLAVE_DB_HOST}
MASTER_DB_HOST: ${MASTER_DB_HOST}
FP_PROD_HOST: ${FP_PROD_HOST}
FP_STG_HOST: ${FP_STG_HOST}
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
    TARGET_HOST=${FP_PROD_HOST}
    ;;
stg)
    echo "ステージングDBにデータを登録します"
    TARGET_HOST=${FP_STG_HOST}
    ;;
*)
    echo "選択が不適切です。"
    return 1
    ;;
esac

cat << EOS
#---------------------------
# リモートホストとの接続確認
#---------------------------
EOS

connected=$(echo "hostname" | remote_execution ${WHO_AM_I} ${TARGET_HOST})
if [ $? -ne 0 ]; then
    echo "${txtred}リモートホスト「${TARGET_HOST}」の接続に失敗しました。config.shを見直してください。${txtreset}"
    exit 1
fi
echo "${txtblue}正常に${connected}に接続しました。${txtreset}"


cat << EOS
#---------------------------
# ORG_IDの確認
#---------------------------
EOS

connect="mysql -u ticketing_ro -pticketing -h ${SLAVE_DB_HOST} -P 3308 -D ticketing"
sql=$(cat << EOS
SELECT * FROM Organization WHERE code = "${CODE}"\G
EOS
)

echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_HOST}

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

connect="mysql -u ticketing_ro -pticketing -h ${SLAVE_DB_HOST} -P 3308 -D ticketing"
sql=$(cat << EOS
SELECT * FROM FamiPortTenant WHERE organization_id = ${ORG_ID}; ;\G
SELECT * FROM FamiPortTicketTemplate WHERE organization_id = ${ORG_ID}\G
EOS
)

echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_HOST}

confirm "DB:ticketingにデータが未作成であることが確認できましたか？(y)"

connect="mysql -u famiport_ro -pfamiport -h ${SLAVE_DB_HOST} -P 3308 -D famiport"
sql=$(cat << EOS
SELECT * FROM FamiPortClient WHERE code= ${FP_TENANT_CODE};
EOS
)

echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_HOST}

confirm "DB:famiportにデータが未作成であることが確認できましたか？(y)"

cat << EOS
#---------------------------
#
# データ登録の実施
#
#---------------------------
EOS

connect="mysql -u ticketing -pticketing -h ${MASTER_DB_HOST} -P 3308 -D ticketing"
sql=$(cat << EOS
BEGIN;
INSERT INTO FamiPortTicketTemplate (template_code,logically_subticket,mappings,organization_id,name)
SELECT template_code, logically_subticket, mappings, ${ORG_ID}, REPLACE(name, 'BC', ${CODE}) FROM FamiPortTicketTemplate WHERE organization_id=56;

INSERT INTO FamiPortTenant (organization_id, name, code, created_at, updated_at)
SELECT id, name, ${FP_TENANT_CODE}, now(), now()  FROM Organization WHERE id = ${ORG_ID};
COMMIT;
EOS
)

echo "${MASTER_DB_HOST}のDB:ticketingに次のSQLを実行します。"
echo ${sql}

confirm "${txtyellow}よろしいですか(y)${txtreset}"


connect="mysql -u ticketing -pticketing -h ${MASTER_DB_HOST} -P 3308 -D ticketing"
sql=$(cat << EOS
BEGIN;
INSERT INTO FamiPortClient (famiport_playguide_id, code, name, prefix, auth_number_required, created_at, updated_at)
VALUES (1, ${FP_TENANT_CODE}, ${ORG_NAME}, RIGHT(${FP_TENANT_CODE}, 3), 0, now(), now());
COMMIT;
EOS
)

echo "${MASTER_DB_HOST}のDB:famiportに次のSQLを実行します。"
echo ${sql}

confirm "${txtyellow}よろしいですか(y)${txtreset}"


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

connect="mysql -u ticketing_ro -pticketing -h ${SLAVE_DB_HOST} -P 3308 -D ticketing"
sql=$(cat << EOS
SELECT * FROM FamiPortTenant WHERE organization_id = ${ORG_ID}; ;\G
SELECT * FROM FamiPortTicketTemplate WHERE organization_id = ${ORG_ID}\G
EOS
)

echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_HOST}

connect="mysql -u famiport_ro -pfamiport -h ${SLAVE_DB_HOST} -P 3308 -D famiport"
sql=$(cat << EOS
SELECT * FROM FamiPortClient WHERE code= ${FP_TENANT_CODE};
EOS
)

echo "${connect} -e '${sql}'" | remote_execution ${WHO_AM_I} ${TARGET_HOST}

confirm "登録内容に問題がないことを確認してください(y)"

cat << EOS
---------------------------
処理が完了しました。
---------------------------
EOS

exit 0
