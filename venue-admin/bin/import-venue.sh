#!/bin/sh

CURRENT=$(dirname $0)
ALTAIR_ROOT=$(dirname $(dirname $(cd $(dirname $0) ; pwd)))
ALTAIR_ROOT=/srv/altair/master

# PREFECTUREとSUB_NAMEはhex encodedで

DIRNAME=$1
BACKEND_XML=$2
FRONTEND_JSON=$3
ORG=$4
PREF=$5
SUB_NAME=$6

# パラメータチェック
if [ "X${DIRNAME}" = "X" ] ; then
    echo "usage: $0 DIRNAME BACKEND_XML FRONTEND_JSON ORG PREF SUB_NAME"
    exit 1
fi

echo "DIRNAME=${DIRNAME}"
echo "BACKEND=${BACKEND_XML}"
echo "FRONTEND=${FRONTEND_JSON}"
echo "ORG=${ORG}"
echo "PREF=${PREF}"
echo "SUB_NAME=${SUB_NAME}"

# DIRNAMEに.が含まれていたりしたらダメ
if [ `echo ${DIRNAME} | grep \\\\. | wc -l` != "0" ] ; then
    echo "Wrong basename: ${DIRNAME}"
    exit 1
fi

SITE=$(${CURRENT}/get-site ${DIRNAME})
VENUE=$(${CURRENT}/get-venue ${DIRNAME})

# SITEが無い = BACKENDを登録する場合
if [ "X$SITE" = "X" ] ; then
    # ORGが存在するかをチェック
    if [ `${CURRENT}/list-organizations | sed 's/\t.*$//' | grep -x ${ORG} | wc -l` = "0" ] ; then
	echo "No such organization: ${ORG}"
	exit 1
    fi
    
    # パラメータチェック
    if [ "X${BACKEND_XML}" = "X" ] ; then
	echo "backend_xml is required.";
	exit 1
    fi
    
    # ファイルの存在を確認
    if [ ! -f ${BACKEND_XML} ] ; then
	echo "No such file: ${BACKEND_XML}"
	exit 1
    fi
    
    # 指定されている場合は、念のためこちらもチェック
    if [ "X$FRONTEND_JSON" != "X" ] ; then
	if [ ! -f ${FRONTEND_JSON} ] ; then
	    echo "No such file: ${FRONTEND_JSON}"
	    exit 1
	fi
    fi
fi

if [ "X$SITE" = "X" ] ; then
    if [ "X$DRY_RUN" != "X" ] ; then
	exit 0
    fi

    # BACKEND
    echo -n "Starting venue_import at " && date
    cat ${ALTAIR_ROOT}/deploy/production/bin/venue_import | \
    sed "s/^if /import codecs\nsys.stdout = codecs.EncodedFile(sys.stdout, 'utf_8')\nif /" | \
    python - \
	-A 10 -O ${ORG} -U ${DIRNAME}/ \
	${ALTAIR_ROOT}/deploy/production/conf/altair.ticketing.admin.ini \
	${BACKEND_XML} 2>&1
    echo -n "Completed at " && date
    
    SITE=$(${CURRENT}/get-site ${DIRNAME})
    VENUE=$(${CURRENT}/get-venue ${DIRNAME})
    if [ "X$SITE" = "X" ] ; then
	echo "maybe backend registration failed."
	exit 1
    fi
    
    # 補足と都道府県名をセット
    ${CURRENT}/update-site-info ${SITE} ${PREF} ${SUB_NAME}
    
    echo ""
    echo "Registered successfully as site=$SITE"
    echo ""
else
    if [ "X$FRONTEND_JSON" = "X" ] ; then
	echo "already registered as site=$SITE"
	exit 1
    fi
fi

if [ "X$FRONTEND_JSON" != "X" ] ; then
    if [ "X$DRY_RUN" != "X" ] ; then
	exit 0
    fi

    # FRONTEND
    echo -n "Starting frontend_venue_import at " && date
    cat ${ALTAIR_ROOT}/deploy/production/bin/frontend_venue_import | \
	sed "s/^if /import codecs\nsys.stdout = codecs.EncodedFile(sys.stdout, 'utf_8')\nif /" | \
	python - \
	-s ${SITE} -U ${DIRNAME}/ \
	${ALTAIR_ROOT}/deploy/production/conf/altair.ticketing.admin.ini \
	${FRONTEND_JSON} 2>&1
    echo -n "Completed at " && date
fi

if [ "X$VENUE" != "X" ] ; then
    echo ""
    echo "See https://service.ticketstar.jp/venues/show/${VENUE}"
fi

exit 0
