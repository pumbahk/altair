#!/bin/sh

if [ "X${ALTAIR_ENVIRONMENT}" = "X" ] ; then
    echo "usage: ALTAIR_ENVIRONMENT=dev $0"
    exit 1
fi

SERVER_ROOT=$(dirname `(cd $(dirname $0) ; pwd)`)
DEPLOY_ROOT=$(dirname $(dirname `(cd $(dirname $0) ; pwd)`))/deploy/${ALTAIR_ENVIRONMENT}

if [ ! -f "${DEPLOY_ROOT}/conf/altair.ticketing.admin.ini" ] ; then
    echo "No altair configuration: ${DEPLOY_ROOT}/conf/altair.ticketing.admin.ini"
    exit 1
fi

exec env HOME=/home/${USER} PATH=/home/${USER}/.nodebrew/current/bin:${PATH} \
node ${SERVER_ROOT}/index.js -p 33080 -d ${DEPLOY_ROOT} -r ${DEPLOY_ROOT}/var/venue-layout --report-to=venue@ticketstar.jp
