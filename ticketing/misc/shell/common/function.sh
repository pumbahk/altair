#!/bin/bash

#---------------------------
# shellディレクトリ内のスクリプトの共通関数の定義
#---------------------------

# 現在処理を実行中のファイルから、相対パス指定でファイルを読み込む
relative_source() {
    local cwd
    cwd=$(cd $(dirname $0) && pwd)
    [ -f "${cwd}/${1}" ] && . "${cwd}/${1}"
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
    ssh -A ${1}@gk1c.vpc.altr.jp ssh -A ${2} "sh"
}

# コンソールにユーザー入力用のプロンプトを出す
ask() {
    local response
    # call with a prompt string or use a default
    read -r -p "${1:->} " response
    echo $response
}