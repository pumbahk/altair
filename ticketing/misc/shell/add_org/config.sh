#!/bin/bash

#---------------------------
# 以下の値は追加するORGの申請内容に合わせて変更してください。
#---------------------------

CODE="WW"
ORG_NAME="株式会社WW" # 25文字以内で設定してください
CONTACT="http://www.h5-official.com/pages/1236135/contact" # 【mailto:メールアドレス】 OR 【問い合わせURL】
REQUIRED_COUPON=false # クーポン機能必要であればtrueにしてください

### chef-repo設定
SUB_DOMAIN="ww"
FQDN="${SUB_DOMAIN}.tstar.jp"
CHEF_REPO_BRANCH="fix/komatsu/tkt4131"

### ロゴ画像のアサイン
PATH_TO_FAVICON="/Users/ts-motoi.a.komatsu/Downloads/WW/favicon.ico" # faviconは必ずfavicon.icoという画像名で配置してください
PATH_TO_PC_LOGO="/Users/ts-motoi.a.komatsu/Downloads/WW/ww_PC.png"
PATH_TO_SP_LOGO="/Users/ts-motoi.a.komatsu/Downloads/WW/ww_SP.png"
PATH_TO_MB_LOGO="/Users/ts-motoi.a.komatsu/Downloads/WW/ww_MB.gif"

FP_TENANT_CODE="00057" # Famiportテナントコード
FP_IMG_DIR_PATH="/Users/ts-motoi.a.komatsu/Downloads/WW_IMG" # Famiport連携用画像ディレクトリ

#---------------------------
# S3の設定
#---------------------------

BUCKET="tstar-dev" # 【tstar】 OR 【tstar-dev】

PATH_TO_S3_CART="s3://${BUCKET}/cart/static"
PATH_TO_S3_ORDERREVIEW="s3://${BUCKET}/orderreview/static"
PATH_TO_S3_FCAUTH="s3://${BUCKET}/fc_auth/static"
PATH_TO_S3_LOTS="s3://${BUCKET}/lots/static"
PATH_TO_S3_COUPON="s3://${BUCKET}/coupon/static"
PATH_TO_S3_USERSITE="s3://${BUCKET}/usersite/static"

#---------------------------
# 各種静的コンテンツのパス
#---------------------------

PATH_TO_STATIC_CART="ticketing/src/altair/app/ticketing/cart/static"
PATH_TO_STATIC_ORDERREVIEW="ticketing/src/altair/app/ticketing/orderreview/static"
PATH_TO_STATIC_FCAUTH="ticketing/src/altair/app/ticketing/fc_auth/static"
PATH_TO_STATIC_LOTS="ticketing/src/altair/app/ticketing/lots/static"
PATH_TO_STATIC_COUPON="ticketing/src/altair/app/ticketing/coupon/static"
PATH_TO_STATIC_ALTAIRCMS="cms/src/altaircms/static"

#---------------------------
# CSSの追記
#---------------------------

NAV_STEP_CSS=$(cat << EOS


/* navi step bar
-------------------------------------------- */
.nav-stepbar ol li {
    background: var(--custom-light-color);
    color: var(--custom-dark-color);
}

.nav-stepbar ol li:after {
    border-left: 10px solid var(--custom-light-color);
}

.nav-stepbar ol li.current {
    background: var(--custom-default-color);
}

.nav-stepbar ol li.current:after {
    border-left: 10px solid var(--custom-default-color);
}
EOS
)


#---------------------------
# Famiport設定
#---------------------------

FP_IMG_STG_SERVER="btfm2-fmz.1a"
FP_IMG_PROD_SERVER="btfm2.1a"
declare -a CURL_STG_OPTIONS=(
    '--user tstarftpsy:9n2ik7fybx ftps://10.132.73.51:990/'
    '--user tstarftpsz:fainwa75it ftps://10.132.73.51:990/'
)
declare -a CURL_PROD_OPTIONS=(
    '--user tstarftps1:rukvh66bw2 ftps://10.132.73.31:990/'
    '--user tstarftps2:bjmvr3hdn9 ftps://10.132.73.41:990/'
)
