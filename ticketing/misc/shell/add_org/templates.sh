#!/bin/bash
set -eu

cat << EOS
#---------------------------
# 処理の概要
#---------------------------

ORG追加のテンプレート作成処理。
ベースとなるディレクトリからファイルのコピー、シムリンクを生成します。
※ ベースの優先度は「__base__ > __scaffold__」です。
※ TKT-5751でテンプレート参照方法を修正しました。
現在は各ORGディレクトリの下にテンプレート・静的コンテンツファイルが存在しない場合は__base__の同階層を参照するようにしています。
現在のところcmsのエラーコンテンツは対応予定なし。理由はコピペされるファイル数が少ないこと・修正が入る機会が低いことからです。

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
CONTACT: ${CONTACT}
FQDN: ${FQDN}

ALTAIR_PATH: ${ALTAIR_PATH}
PATH_TO_FAVICON: ${PATH_TO_FAVICON}
PATH_TO_PC_LOGO: ${PATH_TO_PC_LOGO}
PATH_TO_SP_LOGO: ${PATH_TO_SP_LOGO}
PATH_TO_MB_LOGO: ${PATH_TO_MB_LOGO}

REQUIRED_COUPON: ${REQUIRED_COUPON}
NAV_STEP_CSS: ${NAV_STEP_CSS}
EOS

read -p "テンプレート作成を開始します。続けるにはエンターキーを、中止するには「CTRL＋C」を押してください"

cat << EOS
#---------------------------
# 【手順】cart 画像の配置
#---------------------------
EOS

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_CART}
test -d ${CODE} && rm -rf ${CODE}

mkdir -p ${CODE}/pc/images
mkdir -p ${CODE}/smartphone/images
mkdir -p ${CODE}/mobile/images

test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
test -f ${PATH_TO_SP_LOGO} && cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】orderreview 画像の配置
#---------------------------
EOS

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_ORDERREVIEW}
test -d ${CODE} && rm -rf ${CODE}

mkdir -p ${CODE}/pc/images
mkdir -p ${CODE}/smartphone/images
mkdir -p ${CODE}/mobile/images

test -f ${PATH_TO_ORDERREVIEW_LOGO} && cp ${PATH_TO_ORDERREVIEW_LOGO} ${CODE}/pc/images/logo.png # orderreviewの場合はPCだとロゴのサイズが合わないのでSPのロゴを使用する
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】fc_auth 画像の配置
#---------------------------
EOS

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_FCAUTH}
test -d ${CODE} && rm -rf ${CODE}

mkdir -p ${CODE}/pc/images
mkdir -p ${CODE}/smartphone/images
mkdir -p ${CODE}/mobile/images

test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
test -f ${PATH_TO_SP_LOGO} && cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】lots 画像の配置
#---------------------------
EOS

cd ${ALTAIR_PATH}/${PATH_TO_STATIC_LOTS}
test -d ${CODE} && rm -rf ${CODE}

mkdir -p ${CODE}/pc/images
mkdir -p ${CODE}/smartphone/images
mkdir -p ${CODE}/mobile/images

test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
test -f ${PATH_TO_SP_LOGO} && cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico
test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/mb_logo.gif

cat << EOS
#---------------------------
# 【手順】coupon 画像の配置 (※ 動作確認未実施)
#---------------------------
EOS

if ${REQUIRED_COUPON}; then
    cd ${ALTAIR_PATH}/${PATH_TO_STATIC_COUPON}
    test -d ${CODE} && rm -rf ${CODE}

    mkdir -p ${CODE}/pc/images
    mkdir -p ${CODE}/smartphone/images
    mkdir -p ${CODE}/mobile/images

    test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
    test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
    test -f ${PATH_TO_MB_LOGO} && cp ${PATH_TO_MB_LOGO} ${CODE}/mobile/images/logo_mobile.gif

    #    WEBクーポンはドキュメントが用意されておらず詳細が不明なため、あまりこのシェルスクリプトを信用しないでください。
    #    https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId=880808162
    #    ↑のURLにもあるように、開発者に聞いてください。

    #    以下のファイルに文言を追加する必要があるようです。__base__のファイルに動的に追加できるよう修正すれば良いかと。
    #
    #    /cart/templates/RM/plugins/reserved_number_completion.html
    #    /cart/templates/RM/plugins/reserved_number_mail_complete.html
    #    /orderreview/templates/RM/plugins/reserved_number_completion.html
    #    /orderreview/templates/RM/plugins/reserved_number_mail_complete.html
    #
    #    以下のURLより、ご入場（クーポンのご使用）になれます。
    #    https://${request.host}/coupon/${reserved_number.number}
    #    ${description}

else
    echo "REQUIRED_COUPONが${REQUIRED_COUPON}に設定されているため、スキップします。"
fi

cat << EOS

#---------------------------
# 【手順】extauth テンプレート/画像の配置
#---------------------------
EOS

if ${REQUIRED_EXTAUTH}; then
    # テンプレートの配置
    # 暫定対応でGP（現在（2018/08/03時点）で最新）をベースにしてテンプレートを作成します。
    # コピーしたら、中身色な値を手修正するものがありますので、ご注意ください。
    cd ${ALTAIR_PATH}/ticketing/src/altair/app/ticketing/extauth/templates
    test -d ${CODE} && rm -rf ${CODE}
    mkdir -p ${CODE}/__default__
    cp -r GP/__default__/pc ${CODE}/__default__/pc

    ### replace
    find ${CODE} -type f | xargs sed -i'' -e "s@goodluck-p.tstar.jp@${FQDN}@g"
    find ${CODE} -type f | xargs sed -i'' -e "s@グッドラック・プロモーション@${ORG_NAME}@g"
    find ${CODE} -type f -name "*-e" | xargs rm  # バックアップができることがあるので、その場合消す

    ### simlink
    cd ${CODE}/__default__
    ln -s pc smartphone

    # 静的コンテンツの配置
    cd ${ALTAIR_PATH}/${PATH_TO_STATIC_EXTAUTH}
    test -d ${CODE} && rm -rf ${CODE}
    cp -r __default__ ${CODE}

    test -f ${PATH_TO_PC_LOGO} && cp ${PATH_TO_PC_LOGO} ${CODE}/pc/images/logo.png
    test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/pc/images/favicon.ico
    test -f ${PATH_TO_SP_LOGO} && cp ${PATH_TO_SP_LOGO} ${CODE}/smartphone/images/logo.png
    test -f ${PATH_TO_FAVICON} && cp ${PATH_TO_FAVICON} ${CODE}/smartphone/images/favicon.ico

else
    echo "REQUIRED_EXTAUTHが${REQUIRED_EXTAUTH}に設定されているため、スキップします。"
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
# 色味変更ファイルの配置
#---------------------------
EOS

cat << EOS

:rootによって各ORGのカート画面などの色味が指定できます。
事業の依頼担当者の好みによって色の指定が来ることがあるので、その場合は希望の色味を聞いてやってください。

EOS

declare -a ALL_PATH_TO_ALL_STATIC=(
    "${ALTAIR_PATH}/${PATH_TO_STATIC_CART}/__base__"
    "${ALTAIR_PATH}/${PATH_TO_STATIC_ORDERREVIEW}/__base__"
    "${ALTAIR_PATH}/${PATH_TO_STATIC_FCAUTH}/__base__"
    "${ALTAIR_PATH}/${PATH_TO_STATIC_LOTS}/__base__"
)

if ${REQUIRED_COUPON}; then
    ALL_PATH_TO_ALL_STATIC+=("${ALTAIR_PATH}/${PATH_TO_STATIC_COUPON}/__base__")
fi

set +e
for path in ${ALL_PATH_TO_ALL_STATIC[@]}; do
    echo "${txtyellow}「grep -lr ':root {' ${path}」を実行します。${txtreset}"
    grep -lr ":root {" "${path}"
done

cp_custom_css=$(ask "上記のCSSファイルをコピーし、ORG独自の色味を持たせますか？ [y(持たせる) / その他のキー(持たせない)]> ")
case "${cp_custom_css}" in
y)
    for path in ${ALL_PATH_TO_ALL_STATIC[@]}; do
        for n in $(grep -lr ":root {" "${path}"); do
            org_path=$(echo "${n}" | sed -e "s/__base__/${CODE}/g")
            org_dir=$(dirname "${org_path}");
            mkdir -p "${org_dir}"
            cp "${n}" "${org_path}"
        done
    done
    echo "コピーが完了しました。面倒ですが各cssファイルの「root:」の中身を手書きで書き換えてください。その内どうにかします。"
    ;;
*)
    echo "独自の色味をもたせません。"
    ;;
esac


if [ "${cp_custom_css}" == "y" ]; then
    ch_nav_step_color=$(ask "カートPC画面のナビステップのカラーを:rootと合わせますか？ [y(合わせる) / その他のキー(合わせない)]> ")
    case "${ch_nav_step_color}" in
    y)
        base_css="${ALTAIR_PATH}/${PATH_TO_STATIC_CART}/__base__/pc/css/custom.css"
        org_css="${ALTAIR_PATH}/${PATH_TO_STATIC_CART}/${CODE}/pc/css/custom.css"

        echo "${txtyellow} ${base_css}をコピーした後、末尾にナビステップ用CSSを追記します。${txtreset}"
        org_dir=$(dirname "${org_css}");
        mkdir -p "${org_dir}"
        cp ${base_css} ${org_css}
        echo "${NAV_STEP_CSS}" >> ${org_css};
        ;;
    *)
        echo "色合わせを行いません。"
        ;;
    esac
fi
set -e


cat << EOS
---------------------------
処理が完了しました。
s3_upload.shを実行してください。
---------------------------
EOS

exit 0
