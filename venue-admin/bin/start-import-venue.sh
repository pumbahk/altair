#!/bin/bash -p

MAILFROM=sasao@ticketstar.jp
MAILTO=venue@ticketstar.jp

CURRENT=$(dirname $0)

DRY_RUN=1 ${CURRENT}/import-venue.sh $*

if [ $? != 0 ] ; then
    exit
fi

echo "Starting background process..."
echo "( echo \"From: ${MAILFROM}\" ; echo \"Subject: result of import-venue\" ; echo \"\" ; ${CURRENT}/import-venue.sh $* ) | /usr/sbin/sendmail -f${MAILFROM} ${MAILTO} 1> /dev/null 2> /dev/null &" | /bin/sh
