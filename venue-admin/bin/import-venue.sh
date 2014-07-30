#!/bin/sh

CURRENT=$(dirname $0)

# usage:
# [DRY_RUN=1] import-venue.sh ORG DIRNAME BACKEND_XML [FRONTEND_JSON] [PREFECTURE] [SUB_NAME]

# ex:
# ./import-venue.sh 楽天チケット backend/rakuten-hall.xml
# ./import-venue.sh 楽天チケット backend/rakuten-hall.xml frontend/rakuten-hall/metadata.json

# 最初にbackendだけを登録し、後からfrontendを追加することも可能
# PREFECTUREとSUB_NAMEはhex encodedで

ORG=$1
DIRNAME=$2
BACKEND_XML=$3
FRONTEND_JSON=$4
PREF=$5
SUB_NAME=$6

# パラメータチェック
if [ "X${BACKEND_XML}" = "X" ] ; then
    echo "usage: $0 ORG DIRNAME BACKEND_XML [FRONTEND_JSON]"
    exit 1
fi

# ORGが存在するかをチェック
if [ `${CURRENT}/list-organizations | sed 's/\t.*$//' | grep -x ${ORG} | wc -l` = "0" ] ; then
    echo "No such organization: ${ORG}"
    exit 1
fi

# ファイルの存在を確認
if [ ! -f ${BACKEND_XML} ] ; then
    echo "No such file: ${BACKEND_XML}"
    exit 1
fi

if [ "X$FRONTEND_JSON" != "X" ] ; then
    if [ ! -f ${FRONTEND_JSON} ] ; then
	echo "No such file: ${FRONTEND_JSON}"
	exit 1
    fi
fi

# DIRNAMEに.が含まれていたりしたらダメ
if [ `echo ${DIRNAME} | grep \\\\. | wc -l` != "0" ] ; then
    echo "Wrong basename: ${DIRNAME}"
    exit 1
fi

# 登録済みでないことを確認
SITE=$(${CURRENT}/get-site ${DIRNAME})

if [ "X$SITE" = "X" ] ; then
    if [ "X$DRY_RUN" != "X" ] ; then
	exit 0
    fi

    # BACKEND
    echo -n "Starting venue_import at " && date
    cat /srv/altair/master/deploy/production/bin/venue_import | \
	sed "s/^if /import codecs\nsys.stdout = codecs.EncodedFile(sys.stdout, 'utf_8')\nif /" | \
	python - \
	-A 10 -O ${ORG} -U ${DIRNAME}/ \
	/srv/altair/master/deploy/production/conf/altair.ticketing.admin.ini \
	${BACKEND_XML} 2>&1
    echo -n "Copmleted at " && date
    
    SITE=$(${CURRENT}/get-site ${DIRNAME})
    if [ "X$SITE" = "X" ] ; then
	echo "maybe backend registration failed."
	exit 1
    fi
    
    # 補足と都道府県名をセット
    ${CURRENT}/update-site-info ${SITE} ${PREF} ${SUB_NAME}
    
    echo "registered successfully as site=$SITE"
else
    if [ "X$FRONTEND_JSON" = "X" ] ; then
	echo "already registered as site=$SITE"
	exit 1
    fi
fi

if [ "X$FRONTEND_JSON" != "X" ] ; then
    # FRONTENDは上書きが可能なので重複チェックはしない, 上書きは危険ではあるが...
    FRONTEND_URL=$(${CURRENT}/get-frontend ${SITE})
    
    if [ "X$DRY_RUN" != "X" ] ; then
	exit 0
    fi

    # FRONTEND
    echo -n "Starting frontend_venue_import at " && date
    cat /srv/altair/master/deploy/production/bin/frontend_venue_import | \
	sed "s/^if /import codecs\nsys.stdout = codecs.EncodedFile(sys.stdout, 'utf_8')\nif /" | \
	python - \
	-s ${SITE} -U ${DIRNAME}/ \
	/srv/altair/master/deploy/production/conf/altair.ticketing.admin.ini \
	${FRONTEND_JSON} 2>&1
    echo -n "Copmleted at " && date
fi

exit 0
