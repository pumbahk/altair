#!/bin/bash
set -eu

cat << EOS
#---------------------------
# 処理の概要
#---------------------------

S3へ静的コンテンツをアップロードします。

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
ORG_NAME: ${ORG_NAME}

ALTAIR_PATH: ${ALTAIR_PATH}
PATH_TO_STATIC_CART: ${PATH_TO_STATIC_CART}
PATH_TO_STATIC_ORDERREVIEW: ${PATH_TO_STATIC_ORDERREVIEW}
PATH_TO_STATIC_FCAUTH: ${PATH_TO_STATIC_FCAUTH}
PATH_TO_STATIC_LOTS: ${PATH_TO_STATIC_LOTS}
PATH_TO_STATIC_COUPON: ${PATH_TO_STATIC_COUPON}
PATH_TO_STATIC_ALTAIRCMS: ${PATH_TO_STATIC_ALTAIRCMS}

BUCKET: ${BUCKET}
PATH_TO_S3_CART: ${PATH_TO_S3_CART}
PATH_TO_S3_ORDERREVIEW: ${PATH_TO_S3_ORDERREVIEW}
PATH_TO_S3_FCAUTH: ${PATH_TO_S3_FCAUTH}
PATH_TO_S3_LOTS: ${PATH_TO_S3_LOTS}
PATH_TO_S3_COUPON: ${PATH_TO_S3_COUPON}
PATH_TO_S3_USERSITE: ${PATH_TO_S3_USERSITE}

REQUIRED_COUPON: ${REQUIRED_COUPON}
EOS

read -p "上記の静的コンテンツディレクトリをS3へアップロードします。続けるにはエンターキーを、中止するには「CTRL＋C」を押してください"

cat << EOS
#---------------------------
# 静的コンテンツのアップロード
#---------------------------
EOS

if [ "${BUCKET}" == "tstar" ]; then
    echo "${txtred}本番環境のバケットが選択されています。本当にアップロードしてよいですか？(y)${txtreset}"
    read answer
    if [ "${answer}" != "y" ]; then
        echo "「y」以外が選択されました。処理を中断します。"
        exit 0
    fi
fi

### local, STG
s3_upload ${PATH_TO_S3_CART} ${ALTAIR_PATH}/${PATH_TO_STATIC_CART}
s3_upload ${PATH_TO_S3_ORDERREVIEW} ${ALTAIR_PATH}/${PATH_TO_STATIC_ORDERREVIEW}
s3_upload ${PATH_TO_S3_FCAUTH} ${ALTAIR_PATH}/${PATH_TO_STATIC_FCAUTH}
s3_upload ${PATH_TO_S3_LOTS} ${ALTAIR_PATH}/${PATH_TO_STATIC_LOTS}
s3_upload ${PATH_TO_S3_USERSITE} ${ALTAIR_PATH}/${PATH_TO_STATIC_ALTAIRCMS}

if ${REQUIRED_COUPON}; then
    s3_upload ${PATH_TO_S3_COUPON} ${ALTAIR_PATH}/${PATH_TO_STATIC_COUPON}
fi

cat << EOS
---------------------------
処理が完了しました。
---------------------------
EOS

exit 0
