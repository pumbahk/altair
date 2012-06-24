#!/bin/sh
ROOT=`dirname $0`
if echo $ROOT | grep -v -q '^/'; then
    ROOT="$PWD/$ROOT"
fi
HTTPD=httpd

case $1 in
    start)
        if test -e "${ROOT}/tmp/pid"; then
            echo "Server already running?"
        else
            test -d "${ROOT}/tmp" || mkdir "${ROOT}/tmp"
            env ROOT="${ROOT}" "${HTTPD}" -f "${ROOT}/httpd.test.conf"
        fi
		;;
	stop)
		if test -e "${ROOT}/tmp/pid"; then
			kill -TERM `cat "${ROOT}/tmp/pid"`;
		else
			echo "Server not running";
		fi
		;;
esac
