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

# 確認用プロンプト表示
confirm() {
    local response
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? (y):} " response
    case ${response} in
        y)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# 指定の対象にコマンドをリモート実行
remote_execution() {
    ssh -A ${1}@gk1c.vpc.altr.jp ssh -A deploy2.1a.vpc.altr ssh -A ${2} "sh"
}

# コンソールにユーザー入力用のプロンプトを出す
ask() {
    local response
    # call with a prompt string or use a default
    read -r -p "${1:->} " response
    echo $response
}