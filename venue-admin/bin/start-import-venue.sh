#!/bin/bash -p

MAILFROM=venue@ticketstar.jp
MAILTO=venue@ticketstar.jp

CURRENT=$(dirname $0)

DRY_RUN=1 ${CURRENT}/import-venue.sh "$1" "$2" "$3" "$4" "$5" "$6" "$7"

if [ $? != 0 ] ; then
    exit
fi

echo "Starting background process..."
echo "( ( echo \"From: ${MAILFROM}\" ; echo \"Subject: result of import-venue\" ; echo \"\" ; ${CURRENT}/import-venue.sh \"$1\" \"$2\" \"$3\" \"$4\" \"$5\" \"$6\" ) | /usr/sbin/sendmail -f${MAILFROM} ${MAILTO} ) | /bin/bash 1> /dev/null 2> /dev/null < /dev/null &" | /bin/bash 1> /dev/null 2> /dev/null
