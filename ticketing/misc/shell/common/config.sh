#!/bin/bash

#---------------------------
# shellディレクトリ内のスクリプトの共通設定
#---------------------------

### 各自の開発環境に併せてください
ALTAIR_PATH=~/altair # 各自localのPATHをいれてください
CHEF_REPO_PATH=~/chef-repo/ # 各自localのPATHをいれてください
WHO_AM_I="komatsumo02" # 踏み台サーバー(gk1)以降でwhoamiを実行した結果のユーザー名

### サーバー
STG_SERVER="apmv1-stg.1a.vpc.altr"
PROD_SERVER="btmv1.1c.vpc.altr"

### DBホスト
STANDBY_DB="dbmain.standby.altr"
MASTER_DB="dbmain.master.altr"
STANDBY_DB_FMP="dbfmp.standby.altr"
MASTER_DB_FMP="dbfmp.master.altr"

### DBポート
STANDBY_PORT="3308"
MASTER_PORT="3306"

### テキスト装飾
if [ "${TERM:-dumb}" != "dumb" ]; then
    txtunderline=$(tput sgr 0 1)     # Underline
    txtbold=$(tput bold)             # Bold
    txtred=$(tput setaf 1)           # red
    txtgreen=$(tput setaf 2)         # green
    txtyellow=$(tput setaf 3)        # yellow
    txtblue=$(tput setaf 4)          # blue
    txtreset=$(tput sgr0)            # Reset
else
    txtunderline=""
    txtbold=""
    txtred=""
    txtgreen=""
    txtyellow=""
    txtblue=""
    txtreset=""
fi
