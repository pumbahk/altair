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

# 設定の読み込み
[ -f config.sh ] && . config.sh

### 設定内容の出力
echo REQUIRED_COUPON: ${REQUIRED_COUPON}
echo ALTAIR_PATH: ${ALTAIR_PATH}
echo PATH_TO_STATIC_CART: ${PATH_TO_STATIC_CART}
echo PATH_TO_STATIC_ORDERREVIEW: ${PATH_TO_STATIC_ORDERREVIEW}
echo PATH_TO_STATIC_FCAUTH: ${PATH_TO_STATIC_FCAUTH}
echo PATH_TO_STATIC_LOTS: ${PATH_TO_STATIC_LOTS}
echo PATH_TO_STATIC_COUPON: ${PATH_TO_STATIC_COUPON}
echo PATH_TO_STATIC_ALTAIRCMS: ${PATH_TO_STATIC_ALTAIRCMS}

read -p  "上記の静的コンテンツディレクトリをS3へアップロードします。続けるにはエンターキーを、中止するには「CTRL＋C」を押してください"

cat << EOS
#---------------------------
# 静的コンテンツのアップロード
#---------------------------
EOS

### local, STG
cd ${ALTAIR_PATH}/${PATH_TO_STATIC_CART}; pwd
s3cmd put --exclude '.DS_Store' -P -r ${CODE} s3://tstar-dev/cart/static/ --no-preserve

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_ORDERREVIEW}; pwd
s3cmd put --exclude '.DS_Store' -P -r ${CODE} s3://tstar-dev/orderreview/static/ --no-preserve

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_FCAUTH}; pwd
s3cmd put --exclude '.DS_Store' -P -r ${CODE} s3://tstar-dev/fc_auth/static/ --no-preserve

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_LOTS}; pwd
s3cmd put --exclude '.DS_Store' -P -r ${CODE} s3://tstar-dev/lots/static/ --no-preserve

if ${REQUIRED_COUPON}; then
    cd ${ALTAIR_PATH}/${PATH_TO_STATIC_COUPON}; pwd
    s3cmd put --exclude '.DS_Store' -P -r ${CODE} s3://tstar-dev/coupon/static/ --no-preserve
fi

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_ALTAIRCMS}; pwd
s3cmd put --exclude '.DS_Store' -P -r ${CODE} s3://tstar-dev/usersite/static/ --no-preserve

cat << EOS
---------------------------
処理が完了しました。
---------------------------
EOS

exit 0
