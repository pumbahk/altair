#!/bin/bash
cat << EOS
#---------------------------
# 処理の概要
#---------------------------

chef-repoのコードにDNS、LBの設定を行います。

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
SUB_DOMAIN: ${SUB_DOMAIN}
ORG_NAME: ${ORG_NAME}
FQDN: ${FQDN}
CHEF_REPO_PATH: ${CHEF_REPO_PATH}
CHEF_REPO_BRANCH: ${CHEF_REPO_BRANCH}

REQUIRED_COUPON: ${REQUIRED_COUPON}
EOS

read -p "DNS、LBの設定を開始します。続けるにはエンターキーを、中止するには「CTRL＋C」を押してください"

cat << EOS
#---------------------------
# masterから作業ブランチを作成
#---------------------------
EOS

cd ${CHEF_REPO_PATH}
git pull origin master
git checkout -b ${CHEF_REPO_BRANCH}

cat << EOS
#---------------------------
# 1.Nginxの設定ファイルを作成する
#---------------------------
EOS

if ${REQUIRED_COUPON}; then
    cp cookbooks/loadbalancer/templates/default/sites-available/{leisure,${SUB_DOMAIN}}.tstar.jp.erb
else
    cp cookbooks/loadbalancer/templates/default/sites-available/{tokairadio,${SUB_DOMAIN}}.tstar.jp.erb
fi

ls cookbooks/loadbalancer/templates/default/sites-available/${FQDN}.erb

cat << EOS
#---------------------------
# 2.loadbalancer-tstar.jsonへの追加
#---------------------------
EOS

echo "roles/loadbalancer-tstar.jsonのloadbalancer:domainsの末尾に${FQDN}を追記してください。"
read -p '別ウィンドウを開き「vi roles/loadbalancer-tstar.json」で編集し、完了したらエンターキーを押してください。'

grep -1 -n ${FQDN} roles/loadbalancer-tstar.json
git diff roles/loadbalancer-tstar.json

echo "編集内容に間違いはありませんか？（行末カンマに注意）"
read -p 'よろしければエンターキーを押してください。'

cat << EOS
#---------------------------
# 3. databagの追加
#---------------------------
EOS

# vlentからドメインを置換して作成
sed -e "s/tokairadio/${SUB_DOMAIN}/g" -e "s/東海ラジオ放送事業部/${ORG_NAME}/" data_bags/altair/tokairadio.tstar.jp.json > data_bags/altair/${FQDN}.json

cat << EOS
#---------------------------
# 4. エラーコンテンツの追加
#---------------------------
EOS

# 400番台、500番台のエラーコンテンツを配置。
cp -r cookbooks/loadbalancer/files/default/www/{nbs,${SUB_DOMAIN}}.tstar.jp
ls -l cookbooks/loadbalancer/files/default/www/${FQDN}

cat << EOS
#---------------------------
# 5. gitへの登録とpush
#---------------------------
EOS

echo "設定が完了しました。問題がなければコミットしてプルリクエストを作成してください。"

cat << EOS
---------------------------
※ 注意 ※

extauth、ファンクラブ（fc）を利用しない場合は以下のコマンドで該当箇所を削除してください。

vi cookbooks/loadbalancer/templates/default/sites-available/${SUB_DOMAIN}}.tstar.jp.erb
vi data_bags/altair/${SUB_DOMAIN}}.tstar.jp.json

---------------------------
EOS

exit 0
