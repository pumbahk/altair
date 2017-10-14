#!/bin/bash

cat << EOS
#---------------------------
# 処理の概要
#---------------------------

ORG追加のテンプレート作成処理。
ベースとなるディレクトリからファイルのコピー、シムリンクを生成します。
※ ベースの優先度は「__i18n__　> __scaffold__」です。

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
ALTAIR_PATH: ${ALTAIR_PATH}
CODE: ${CODE}
ORG_NAME: ${ORG_NAME}
CONTACT: ${CONTACT}
REQUIRED_COUPON: ${REQUIRED_COUPON}
PATH_TO_FAVICON: ${PATH_TO_FAVICON}
PATH_TO_PC_LOGO: ${PATH_TO_PC_LOGO}
PATH_TO_SP_LOGO: ${PATH_TO_SP_LOGO}
PATH_TO_MB_LOGO: ${PATH_TO_MB_LOGO}
EOS

read -p "テンプレート作成を開始します。続けるにはエンターキーを、中止するには「CTRL＋C」を押してください"

cat << EOS
#---------------------------
# 【手順】cartのテンプレート配備
#---------------------------
EOS

# ディレクトリを作って移動し、整備する
cd ${ALTAIR_PATH}/ticketing/src/altair/app/ticketing/cart/templates
base=`choose_base`

echo "`pwd`/${CODE}は${base}で作成します。"

test ! -d ${CODE} && mkdir ${CODE}
cd ${CODE}
test ! -L pc         && ln -s ../${base}/pc .               # 特殊仕様がなければシムリンク
test ! -L smartphone && ln -s ../${base}/smartphone .       # 特殊仕様がなければシムリンク
test ! -L mobile     && ln -s ../${base}/mobile .           # 特殊仕様がなければシムリンク
test ! -L plugins    && ln -s ../${base}/plugins .          # 特殊仕様がなければシムリンク
test ! -d fc_auth    && cp -r ../${base}/fc_auth .          # カスタマイズ可能
test ! -d includes   && cp -r ../${base}/includes .         # カスタマイズ可能

# 静的コンテンツの配置
cd ${ALTAIR_PATH}/${PATH_TO_STATIC_CART}

echo "`pwd`/${CODE}は${base}で作成します。"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

# ロゴ画像の配置
cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】orderreviewのテンプレート配置
#---------------------------
EOS

cd ${ALTAIR_PATH}/ticketing/src/altair/app/ticketing/orderreview/templates
base=`choose_base`

echo "`pwd`/${CODE}は${base}で作成します。"

test ! -d ${CODE} && mkdir ${CODE}
cd ${CODE}
test ! -L pc         && ln -s ../${base}/pc .               # 特殊仕様がなければシムリンク
test ! -L smartphone && ln -s pc smartphone                      # 特殊仕様がなければシムリンク
test ! -L mobile     && ln -s ../${base}/mobile .           # 特殊仕様がなければシムリンク
test ! -L plugins    && ln -s ../${base}/plugins .           # 特殊仕様がなければシムリンク
test ! -d fc_auth    && cp -r ../${base}/fc_auth .          # カスタマイズ可能
test ! -d includes    && cp -r ../${base}/includes .          # カスタマイズ可能

# 静的コンテンツの配置
cd ${ALTAIR_PATH}/${PATH_TO_STATIC_ORDERREVIEW}
test -d ${CODE} && rm -rf ${CODE}

echo "`pwd`/${CODE}は${base}で作成します。"

cp -r ${base} ${CODE}

# ディレクトリがない場合作る
test ! -d ${CODE}/mobile/images && mkdir -p ${CODE}/mobile/images

# ロゴ画像の配置
cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】fc_authの画像配置
#---------------------------
EOS

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_FCAUTH}
base=`choose_base`

echo "`pwd`/${CODE}は${base}で作成します。"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

# ディレクトリがない場合作る
test ! -d ${CODE}/pc/images && mkdir -p ${CODE}/pc/images
test ! -d ${CODE}/smartphone/images && mkdir -p ${CODE}/smartphone/images
test ! -d ${CODE}/mobile/images && mkdir -p ${CODE}/mobile/images

# ロゴ画像の配置
cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】lots のテンプレート配置手順
#---------------------------
EOS

cd ${ALTAIR_PATH}/ticketing/src/altair/app/ticketing/lots/templates
base=`choose_base`

echo "`pwd`/${CODE}は${base}で作成します。"

test ! -d ${CODE} && mkdir ${CODE}
cd ${CODE}
test ! -L pc         && ln -s ../${base}/pc .                        # 特殊仕様がなければシムリンク
test ! -L smartphone && ln -s ../${base}/smartphone .                # 特殊仕様がなければシムリンク
test ! -L mobile     && ln -s ../${base}/mobile .                    # 特殊仕様がなければシムリンク
test ! -L fc_auth    && ln -s ../../../cart/templates/${CODE}/fc_auth .   # カートのfc_authに向ける
test ! -d includes   && cp -r ../${base}/includes .                  # カスタマイズ可能

# 静的コンテンツの配置
cd ${ALTAIR_PATH}/${PATH_TO_STATIC_LOTS}

echo "`pwd`/${CODE}は${base}で作成します。"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

# ロゴ画像の配置
cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/img/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】coupon のテンプレート配置手順 (※ 動作確認未実施)
#---------------------------
EOS

if ${REQUIRED_COUPON}; then

    cd ${ALTAIR_PATH}/ticketing/src/altair/app/ticketing/coupon/templates
    base=`choose_base`

    echo "`pwd`/${CODE}は${base}で作成します。"

    test -d ${CODE} && rm -rf ${CODE}
    cp -r ${base} ${CODE}

    # 静的コンテンツの配置
    cd ${ALTAIR_PATH}/${PATH_TO_STATIC_COUPON}
    base=`choose_base`

    echo "`pwd`/${CODE}は${base}で作成します。"

    test -d ${CODE} && rm -rf ${CODE}
    cp -r ${base} ${CODE}

    # ロゴ画像の配置
    cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
    cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
    cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/logo_mobile.gif

    # cart/orderreview の template 下の下記ファイルを追加
    cat << 'EOT' > ../cart/templates/RM/plugins/reserved_number_completion.html
以下のURLより、ご入場（クーポンのご使用）になれます。<br/>
<a href="https://${request.host}/coupon/${reserved_number.number}">https://${request.host}/coupon/${reserved_number.number}</a>
<p/>
${description}
EOT

    cat << 'EOT' > ../cart/templates/RM/plugins/reserved_number_mail_complete.html
以下のURLより、ご入場（クーポンのご使用）になれます。
https://${request.host}/coupon/${reserved_number.number}
${description}
EOT

    cat << 'EOT' > ../orderreview/templates/RM/plugins/reserved_number_completion.html
以下のURLより、ご入場（クーポンのご使用）になれます。<br/>
<a href="https://${request.host}/coupon/${reserved_number.number}">https://${request.host}/coupon/${reserved_number.number}</a>
<p/>
${description}
EOT

    cat << 'EOT' > ../orderreview/templates/RM/plugins/reserved_number_mail_complete.html
以下のURLより、ご入場（クーポンのご使用）になれます。
https://${request.host}/coupon/${reserved_number.number}
${description}
EOT

else
    echo "REQUIRED_COUPONが${REQUIRED_COUPON}に設定されているため、スキップします。"
fi

cat << EOS
#---------------------------
# 【手順】cmsのエラーコンテンツ配置手順
#---------------------------
EOS

# テンプレートの配置
cd ${ALTAIR_PATH}/cms/src/altaircms/templates/usersite/errors
base=`choose_base`

echo "`pwd`/${CODE}は${base}で作成します。"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

#### replace
find ${CODE} -type f | xargs sed -i'' -e "s@##CODE##@${CODE}@g"
find ${CODE} -type f | xargs sed -i'' -e "s@##ORG_NAME##@${ORG_NAME}@g"
find ${CODE} -type f | xargs sed -i'' -e "s|##CONTACT##|${CONTACT}|g"       # お問い合わせの【URL】または【mailto:メールアドレス】
find ${CODE} -type f -name "*-e" | xargs rm                                 # バックアップができることがあるので、その場合消す

# 静的コンテンツの配置
cd ${ALTAIR_PATH}/${PATH_TO_STATIC_ALTAIRCMS}
base=`choose_base`

echo "`pwd`/${CODE}は${base}で作成します。"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

# ロゴ画像の配置
cp ${PATH_TO_PC_LOGO} ${CODE}/img/logo.png
cp ${PATH_TO_FAVICON} ${CODE}/img/favicon.ico

cat << EOS
---------------------------
処理が完了しました。

色味の変更など調整を行った後、
s3_upload.shを実行してください。
---------------------------
EOS

exit 0
