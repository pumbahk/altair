#!/bin/bash
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

# 設定・関数の読み込み
CWD=$(cd $(dirname $0) && pwd)
[ -f ${CWD}/config.sh ] && . ${CWD}/config.sh
[ -f ${CWD}/function.sh ] && . ${CWD}/function.sh

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
