#!/bin/sh

source ./config

if [ -d certs ] ; then
  echo "please remove certs directory before process."
  exit
fi

if [ -f $DEST ] ; then
  echo "please remove ${DEST} file before process."
  exit
fi

if [ ! -r certs/$DOMAIN/privkey.pem ] ; then
  echo "Extracting private key from Java App source..."
  mkdir -p certs/$DOMAIN
  openssl pkcs12 -in ../src/main/resources/localhost.p12 -nocerts -nodes -password pass:secret -out certs/$DOMAIN/privkey.pem 2> /dev/null
fi

./dehydrated/dehydrated -c -f ./config.dehydrated -t dns-01 --hook ./hook.sh -d $DOMAIN

if [ ! -f $DEST ] ; then
  echo "Failure"
fi

echo "Success"
keytool -list -keystore $DEST -storepass $KEYSTORE_PASSWORD -v -J-Duser.language=en | egrep -e "Alias|Valid|CN=|\*" | uniq

/bin/echo -n "Uploading keystore to S3... "
aws s3 cp $DEST $KEYSTORE_LOCATION

rm $DEST
rm -r certs

echo "complete."
