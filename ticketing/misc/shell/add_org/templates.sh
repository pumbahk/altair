#!/bin/bash
set -eu

cat << EOS
#---------------------------
# 処理の概要
#---------------------------

ORG追加のテンプレート作成処理。
ベースとなるディレクトリからファイルのコピー、シムリンクを生成します。
※ ベースの優先度は「__base__ > __scaffold__」です。

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
CONTACT: ${CONTACT}

ALTAIR_PATH: ${ALTAIR_PATH}
PATH_TO_FAVICON: ${PATH_TO_FAVICON}
PATH_TO_PC_LOGO: ${PATH_TO_PC_LOGO}
PATH_TO_SP_LOGO: ${PATH_TO_SP_LOGO}
PATH_TO_MB_LOGO: ${PATH_TO_MB_LOGO}

REQUIRED_COUPON: ${REQUIRED_COUPON}
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

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

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

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

# ロゴ画像の配置
test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
test -f ${PATH_TO_SP_LOGO} && cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】orderreviewのテンプレート配置
#---------------------------
EOS

cd ${ALTAIR_PATH}/ticketing/src/altair/app/ticketing/orderreview/templates
base=`choose_base`

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

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

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

cp -r ${base} ${CODE}

# ディレクトリがない場合作る
test ! -d ${CODE}/mobile/images && mkdir -p ${CODE}/mobile/images

# ロゴ画像の配置
test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】fc_authの画像配置
#---------------------------
EOS

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_FCAUTH}
base=`choose_base`

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

# ディレクトリがない場合作る
test ! -d ${CODE}/pc/images && mkdir -p ${CODE}/pc/images
test ! -d ${CODE}/smartphone/images && mkdir -p ${CODE}/smartphone/images
test ! -d ${CODE}/mobile/images && mkdir -p ${CODE}/mobile/images

# ロゴ画像の配置
test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
test -f ${PATH_TO_SP_LOGO} && cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】lots のテンプレート配置手順
#---------------------------
EOS

cd ${ALTAIR_PATH}/ticketing/src/altair/app/ticketing/lots/templates
base=`choose_base`

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

test ! -d ${CODE} && mkdir ${CODE}
cd ${CODE}
test ! -L pc         && ln -s ../${base}/pc .                        # 特殊仕様がなければシムリンク
test ! -L smartphone && ln -s ../${base}/smartphone .                # 特殊仕様がなければシムリンク
test ! -L mobile     && ln -s ../${base}/mobile .                    # 特殊仕様がなければシムリンク
test ! -L fc_auth    && ln -s ../../../cart/templates/${CODE}/fc_auth .   # カートのfc_authに向ける
test ! -d includes   && cp -r ../${base}/includes .                  # カスタマイズ可能

# 静的コンテンツの配置
cd ${ALTAIR_PATH}/${PATH_TO_STATIC_LOTS}

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

# ロゴ画像の配置
test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
test -f ${PATH_TO_SP_LOGO} && cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/img/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】coupon のテンプレート配置手順 (※ 動作確認未実施)
#---------------------------
EOS

if ${REQUIRED_COUPON}; then

    cd ${ALTAIR_PATH}/ticketing/src/altair/app/ticketing/coupon/templates
    base=`choose_base`

    echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtyellow}"

    test -d ${CODE} && rm -rf ${CODE}
    cp -r ${base} ${CODE}

    # 静的コンテンツの配置
    cd ${ALTAIR_PATH}/${PATH_TO_STATIC_COUPON}
    base=`choose_base`

    echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

    test -d ${CODE} && rm -rf ${CODE}
    cp -r ${base} ${CODE}

    # ロゴ画像の配置
    test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
    test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
    test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/logo_mobile.gif

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

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

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

echo "${txtyellow}`pwd`/${CODE}は${base}で作成します。${txtreset}"

test -d ${CODE} && rm -rf ${CODE}
cp -r ${base} ${CODE}

# ロゴ画像の配置
test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/img/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/img/favicon.ico


cat << EOS
#---------------------------
# 色味変更ファイルの検知
#---------------------------
EOS

cat << EOS

基本的に色味の変更はCSSファイルの「:root」の変更で行っています。
事業部からの要望に合わせて、適宜追加調整を行ってください。

EOS

declare -a ALL_PATH_TO_ALL_STATIC=(
    "${ALTAIR_PATH}/${PATH_TO_STATIC_CART}/${CODE}"
    "${ALTAIR_PATH}/${PATH_TO_STATIC_ORDERREVIEW}/${CODE}"
    "${ALTAIR_PATH}/${PATH_TO_STATIC_FCAUTH}/${CODE}"
    "${ALTAIR_PATH}/${PATH_TO_STATIC_LOTS}/${CODE}"
    "${ALTAIR_PATH}/${PATH_TO_STATIC_ALTAIRCMS}/${CODE}"
)

if ${REQUIRED_COUPON}; then
    ALL_PATH_TO_ALL_STATIC+=("${ALTAIR_PATH}/${PATH_TO_STATIC_COUPON}/${CODE}")
fi

set +e
for path in ${ALL_PATH_TO_ALL_STATIC[@]}; do
    echo "${txtyellow}「grep -lr ':root {' ${path}」を実行します。${txtreset}"
    grep -lr ":root {" "${path}"
done

ch_nav_step_color=$(ask "ナビステップのカラーを:rootと合わせますか？ [y(合わせる) / その他のキー(合わせない)]> ")
case "${ch_nav_step_color}" in
y)
    for path in ${ALL_PATH_TO_ALL_STATIC[@]}; do
        echo "${txtyellow}「find ${path}" -name "custom.css」で検知されたファイルの末尾にナビステップ用CSSを追記します。${txtreset}"
        for n in $(find "${path}" -name "custom.css"); do echo "${NAV_STEP_CSS}" >> ${n}; done
    done
    ;;
*)
    echo "色合わせを行いません。"
    ;;
esac
set -e

cat << EOS
---------------------------
処理が完了しました。

色味の変更など調整を行った後、
s3_upload.shを実行してください。
---------------------------
EOS

exit 0
