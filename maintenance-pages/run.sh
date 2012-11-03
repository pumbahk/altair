#!/bin/sh
ROOT=`dirname $0`
if echo $ROOT | grep -v -q '^/'; then
    ROOT="$PWD/$ROOT"
fi

HTTPD=httpd

stop() {
    if test -e "${ROOT}/var/run/pid"; then
        PID=`cat "${ROOT}/var/run/pid"`
        kill -TERM ${PID}
        while ps -p ${PID} 2>&1 >/dev/null; do
            sleep 1
        done
    else
        echo "Server not running";
    fi
}

start() {
    if test -e "${ROOT}/var/run/pid"; then
        echo "Server already running?"
    else
        test -d "${ROOT}/var/run" || mkdir -p "${ROOT}/var/run"
        test -d "${ROOT}/var/log" || mkdir -p "${ROOT}/var/log"
        FLAGS=
        if test -e "${MODULE_DIR}/mod_log_config.so"; then
            FLAGS="${FLAGS} -DLOAD_LOG_CONFIG"
        fi
        if test -e "${MODULE_DIR}/mod_access.so"; then
            FLAGS="${FLAGS} -DLOAD_ACCESS"
        fi
        if test -e "${MODULE_DIR}/mod_authz_host.so"; then
            FLAGS="${FLAGS} -DLOAD_AUTHZ_HOST"
        fi
        env ROOT="${ROOT}" MODULE_DIR="${MODULE_DIR}" MIME_TYPE_FILE="${MIME_TYPE_FILE}" "${HTTPD}" ${FLAGS} ${EXTRA_ARGS} -f "${ROOT}/etc/httpd.conf"
    fi
}

case $1 in
    start)
        start
		;;
	stop)
        stop
		;;
	restart)
        stop
        start
		;;
esac
