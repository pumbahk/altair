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

exec env DEPLOY_ROOT=${DEPLOY_ROOT} \
LISTEN_PORT=33080 \
HTTPD_ROOT=${SERVER_ROOT}/etc \
APACHE_LOCK_DIR=${SERVER_ROOT}/var \
APACHE_PID_FILE=${SERVER_ROOT}/var/apache2.pid \
APACHE_LOG_DIR=${SERVER_ROOT}/var/log \
APACHE_RUN_USER=${USER} \
APACHE_RUN_GROUP=${GROUP} \
/usr/sbin/apache2 -f ${SERVER_ROOT}/etc/apache2.conf -d ${SERVER_ROOT} -DFOREGROUND
