#!/bin/sh

CURRENT=$(dirname $0)

# PREFECTUREとSUB_NAMEはhex encodedで

BACKEND_XML=$1
FRONTEND_JSON=$2
ORG=$3
PREF=$4
SUB_NAME=$5
BACKEND_DIRNAME=$6
FRONTEND_DIRNAME=$7

# パラメータチェック
if [ "X${BACKEND_XML}" = "X" ] ; then
    echo "usage: $0 BACKEND_XML FRONTEND_JSON ORG PREF SUB_NAME BACKEND_DIRNAME FRONTEND_DIRNAME"
    exit 1
fi

echo "BACKEND=${BACKEND_XML}"
echo "FRONTEND=${FRONTEND_JSON}"
echo "ORG=${ORG}"
echo "PREF=${PREF}"
echo "SUB_NAME=${SUB_NAME}"
echo "BACKEND_DIRNAME=${BACKEND_DIRNAME}"
echo "FRONTEND_DIRNAME=${FRONTEND_DIRNAME}"

# DIRNAMEに.が含まれていたりしたらダメ
if [ "X${BACKEND_DIRNAME}" = "X" ] ; then
    echo "backend dirname is required."
    exit 1
fi
if [ `echo ${BACKEND_DIRNAME} | grep \\\\. | wc -l` != "0" ] ; then
    echo "Wrong backend dirname: ${BACKEND_DIRNAME}"
    exit 1
fi

if [ "X$FRONTEND_JSON" != "X" ] ; then
    if [ "X${FRONTEND_DIRNAME}" = "X" ] ; then
	echo "frontend dirname is required."
	exit 1
    fi
    
    # DIRNAMEに.が含まれていたりしたらダメ
    if [ `echo ${FRONTEND_DIRNAME} | grep \\\\. | wc -l` != "0" ] ; then
	echo "Wrong frontend dirname: ${FRONTEND_DIRNAME}"
	exit 1
    fi
fi

# ファイルの存在を確認
if [ ! -f ${BACKEND_XML} ] ; then
    echo "No such file: ${BACKEND_XML}"
    exit 1
fi

# ORGが存在するかをチェック
if [ `${CURRENT}/list-organizations | sed 's/\t.*$//' | grep -x "${ORG}" | wc -l` = "0" ] ; then
    echo "No such organization: ${ORG}"
    exit 1
fi

if [ "X$FRONTEND_JSON" != "X" ] ; then
    # ファイルの存在を確認
    if [ ! -f ${FRONTEND_XML} ] ; then
	echo "No such file: ${FRONTEND_XML}"
	exit 1
    fi
fi

SITE=$(${CURRENT}/get-site ${BACKEND_DIRNAME})
VENUE=$(${CURRENT}/get-venue ${BACKEND_DIRNAME})
if [ "X$SITE" != "X" ] ; then
    echo "already registered as site=$SITE"
    exit 1
fi

if [ "X$DRY_RUN" != "X" ] ; then
    exit 0
fi

echo -n "Starting venue_import at " && date
    cat ${DEPLOY_ROOT}/bin/venue_import | \
    sed "s/^if /import codecs\nsys.stdout = codecs.EncodedFile(sys.stdout, 'utf_8')\nif /" | \
    env LC_ALL=en_US.UTF-8 python - \
	-A 10 -O "${ORG}" -U ${BACKEND_DIRNAME} -P "${PREF}" \
	${DEPLOY_ROOT}/conf/altair.ticketing.admin.ini \
	${BACKEND_XML} 2>&1
echo -n "Completed at " && date

SITE=$(${CURRENT}/get-site ${BACKEND_DIRNAME})
VENUE=$(${CURRENT}/get-venue ${BACKEND_DIRNAME})
if [ "X$SITE" = "X" ] ; then
    echo "maybe backend registration failed."
    exit 1
fi

# 補足と都道府県名をセット
${CURRENT}/update-site-info ${SITE} ${PREF} ${SUB_NAME}

# フロントエンド
if [ "X$FRONTEND_JSON" != "X" ] ; then
    ${CURRENT}/register-frontend.sh ${SITE} ${FRONTEND_JSON} ${FRONTEND_DIRNAME}
fi

echo ""
echo "Registered successfully as site=$SITE"
echo ""
echo "See https://service.ticketstar.jp/venues/show/$VENUE"

exit 0
