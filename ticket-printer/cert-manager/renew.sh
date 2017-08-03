#!/bin/sh

source ./config

if [ ! -f certs/$DOMAIN/privkey.pem ] ; then
  echo "private key is not found: certs/${DOMAIN}/privkey.pem"
  exit
fi

if [ -f $DEST ] ; then
  echo "please remove ${DEST} file before process."
  exit
fi

./dehydrated/dehydrated -c -f ./config.dehydrated -t dns-01 --hook ./hook.sh -d $DOMAIN

if [ -f $DEST ] ; then
  echo "Success"
  keytool -list -keystore $DEST -storepass $KEYSTORE_PASSWORD -v -J-Duser.language=en | egrep -e "Alias|Valid|CN=|\*" | uniq
else
  echo "Failure"
fi
