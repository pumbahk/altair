#!/bin/sh
HTTPD=httpd

case $1 in
    start)
        if test -e "${PWD}/tmp/pid"; then
            echo "Server already running?"
        else
            test -d "${PWD}/tmp" || mkdir "${PWD}/tmp"
            "${HTTPD}" -f "${PWD}/httpd.test.conf"
        fi
		;;
	stop)
		if test -e "${PWD}/tmp/pid"; then
			kill -TERM `cat "${PWD}/tmp/pid"`;
		else
			echo "Server not running";
		fi
		;;
esac
