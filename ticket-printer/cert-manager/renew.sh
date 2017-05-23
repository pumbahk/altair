#!/bin/sh

if [ -f keystore ] ; then
  echo "please remove keystore file before process."
  exit
fi


./dehydrated/dehydrated -c -f ./config -t dns-01 --hook ./hook.sh \
-d localhost.altair-printer.tk
