#!/bin/bash

BASEDIR=$(cd $(dirname $0) && pwd)

source $BASEDIR/config

if [ ! -x $BASEDIR/dehydrated/dehydrated ] ; then
  echo "please setup first."
  exit
fi

if [ ! -d $BASEDIR/accounts ] ; then
  echo "please setup first."
  exit
fi

if [ -d $BASEDIR/certs ] ; then
  echo "please remove certs directory before process."
  exit
fi

if [ -f $BASEDIR/$DEST ] ; then
  echo "please remove ${DEST} file before process."
  exit
fi

if [ ! -r $BASEDIR/certs/$DOMAIN/privkey.pem ] ; then
  echo "Extracting private key from Java App source..."
  mkdir -p $BASEDIR/certs/$DOMAIN
  openssl pkcs12 -in $BASEDIR/../src/main/resources/localhost.p12 -nocerts -nodes -password pass:secret -out $BASEDIR/certs/$DOMAIN/privkey.pem 2> /dev/null
fi

(cd $BASEDIR ; ./dehydrated/dehydrated -c -f ./config.dehydrated -t dns-01 --hook ./hook.sh -d $DOMAIN )

if [ ! -f $BASEDIR/$DEST ] ; then
  echo "Failure"
else
  echo "Success"
  keytool -list -keystore $BASEDIR/$DEST -storepass $KEYSTORE_PASSWORD -v -J-Duser.language=en | egrep -e "Alias|Valid|CN=|\*" | uniq

  /bin/echo -n "Uploading keystore to S3... "
  aws s3 cp $BASEDIR/$DEST $KEYSTORE_LOCATION
  rm $BASEDIR/$DEST
fi

rm -r $BASEDIR/certs

echo "complete."
