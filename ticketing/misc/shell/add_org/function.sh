#!/bin/bash

#---------------------------
# 関数の定義
#---------------------------

# テンプレート・静的コンテンツのベースを決定
choose_base() {
    if [ -e __base__ ]; then
        echo "__base__"
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

    if [ ! -d "${local_path}" ]; then
        echo "ローカルディレクトリ: ${local_path}が存在していません。"
        return 0
    fi

    # S3に既存のディレクトリがあるか確認
    is_exist=`s3cmd ls "${s3_path}/${CODE}"`
    if [ -n "${is_exist}" ]; then
        echo "アップロード先: ${s3_path}/${CODE}がすでに存在しています。"
        echo "[ d:削除してからアップロード o:上書きしてアップロード その他のキー:スキップ ]"
        read answer
        case "${answer}" in
        d)
            echo "削除してからアップロードします。"
            s3cmd del -r "${s3_path}/${CODE}"
            ;;
        o)
            echo "既存のアップロード先を上書きする形式で処理を続行します。"
            ;;
        *)
            echo "アップロードをスキップします。"
            return 0
            ;;
        esac
    fi

    cd ${local_path}; pwd
    s3cmd put --exclude ".DS_Store" -P -r ${CODE} "${s3_path}/" --no-preserve
    return 0
}