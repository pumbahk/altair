#!/bin/sh

SERVER_ROOT=$(dirname `(cd $(dirname $0) ; pwd)`)

GID=`grep ^${USER}: /etc/passwd | cut -d ":" -f 4`
GROUP=`grep :${GID}: /etc/group | cut -d ":" -f 1`

LISTEN_PORT=33080 \
HTTPD_ROOT=${SERVER_ROOT}/etc \
APACHE_LOCK_DIR=${SERVER_ROOT}/var \
APACHE_PID_FILE=${SERVER_ROOT}/var/apache2.pid \
APACHE_LOG_DIR=${SERVER_ROOT}/var/log \
APACHE_RUN_USER=${USER} \
APACHE_RUN_GROUP=${GROUP} \
/usr/sbin/apache2 -f ${SERVER_ROOT}/etc/apache2.conf -d ${SERVER_ROOT}
