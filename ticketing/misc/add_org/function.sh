#!/bin/bash

#---------------------------
# 関数の定義
#---------------------------

# テンプレート・静的コンテンツのベースを決定
choose_base() {
    if [ -e __i18n__ ]; then
        echo "__i18n__"
    elif [ -e __scaffold__ ]; then
        echo "__scaffold__"
    else
        echo "ベースとなるディレクトリがありません。"
        exit 1
    fi
}

# S3に静的コンテンツをアップロード
# 既存ディレクトリの確認・削除判定付き
s3_upload() {
    # 引数解析
    local s3_path="${1}"
    local local_path="${2}"

    # S3に既存のディレクトリがあるか確認
    is_exist=`s3cmd ls ${s3_path}`
    if [ -n "${is_exist}" ]; then
        echo "アップロード先: ${s3_path}がすでに存在しています。"
        echo '削除してから処理を続行しますか？(y)'
        read answer
        case "${answer}" in
        y)
            s3cmd del -r ${s3_path}
            echo "削除しました。"
            ;;
        *)
            echo "既存のアップロード先を上書きする形式で処理を続行します。"
            ;;
        esac
    fi

    cd ${local_path}; pwd
    s3cmd put --exclude '.DS_Store' -P -r ${CODE} ${s3_path} --no-preserve
}