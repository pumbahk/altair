#!/bin/bash

#---------------------------
# 以下の値は追加するORGの申請内容に合わせて変更してください。
#---------------------------

CODE="KZ"
ORG_NAME="オペラシアターこんにゃく座チケットサービス"
CONTACT="mailto:ticket@konnyakuza.com" # 【mailto:メールアドレス】 OR 【問い合わせURL】
ALTAIR_PATH=~/altair # 各自localのPATHをいれてください
REQUIRED_COUPON=false # クーポン機能必要であればtrueにしてください

### ロゴ画像のアサイン
PATH_TO_FAVICON="/Users/ts-motoi.a.komatsu/Downloads/favicon.ico" # faviconは必ずfavicon.icoという画像名で配置してください
PATH_TO_PC_LOGO="/Users/ts-motoi.a.komatsu/Downloads/PC_header+.png"
PATH_TO_SP_LOGO="/Users/ts-motoi.a.komatsu/Downloads/SP_header+.png"
PATH_TO_MB_LOGO="/Users/ts-motoi.a.komatsu/Downloads/MB_header-.gif"

#---------------------------
# S3の設定
#---------------------------

BUCKET="tstar-dev" # 【tstar】 OR 【tstar-dev】

PATH_TO_S3_CART="s3://${BUCKET}/cart/static/${CODE}/"
PATH_TO_S3_ORDERREVIEW="s3://${BUCKET}/orderreview/static/${CODE}/"
PATH_TO_S3_FCAUTH="s3://${BUCKET}/fc_auth/static/${CODE}/"
PATH_TO_S3_LOTS="s3://${BUCKET}/lots/static/${CODE}/"
PATH_TO_S3_COUPON="s3://${BUCKET}/coupon/static/${CODE}/"
PATH_TO_S3_USERSITE="s3://${BUCKET}/usersite/static/${CODE}/"

#---------------------------
# 各種静的コンテンツのパス
#---------------------------

PATH_TO_STATIC_CART="ticketing/src/altair/app/ticketing/cart/static"
PATH_TO_STATIC_ORDERREVIEW="ticketing/src/altair/app/ticketing/orderreview/static"
PATH_TO_STATIC_FCAUTH="ticketing/src/altair/app/ticketing/fc_auth/static"
PATH_TO_STATIC_LOTS="ticketing/src/altair/app/ticketing/lots/static"
PATH_TO_STATIC_COUPON="ticketing/src/altair/app/ticketing/coupon/static"
PATH_TO_STATIC_ALTAIRCMS="cms/src/altaircms/static"