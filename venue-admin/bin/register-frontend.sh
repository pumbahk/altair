#!/bin/sh

CURRENT=$(dirname $0)
ALTAIR_ROOT=$(dirname $(dirname $(cd $(dirname $0) ; pwd)))

SITE=$1
FRONTEND_JSON=$2
DIRNAME=$3

# パラメータチェック
if [ "X${DIRNAME}" = "X" ] ; then
    echo "usage: $0 SITE FRONTEND_JSON DIRNAME"
    exit 1
fi

echo "SITE=${SITE}"
echo "FRONTEND=${FRONTEND_JSON}"
echo "DIRNAME=${DIRNAME}"

# DIRNAMEの重複チェックはしていない、重複したら上書きされるだけ

echo -n "Starting frontend_venue_import at " && date
cat ${ALTAIR_ROOT}/deploy/production/bin/frontend_venue_import | \
    sed "s/^if /import codecs\nsys.stdout = codecs.EncodedFile(sys.stdout, 'utf_8')\nif /" | \
    python - \
    -s ${SITE} -U ${DIRNAME}/ \
    ${ALTAIR_ROOT}/deploy/production/conf/altair.ticketing.admin.ini \
    ${FRONTEND_JSON} 2>&1
echo -n "Completed at " && date
