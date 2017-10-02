#!/bin/bash

BASEDIR=$(cd $(dirname $0) && pwd)

source $BASEDIR/config

if [ X`which git` = X ] ; then
  echo "ERROR: git command is not available."
  HAS_ERRORS=1
fi

if [ X`which openssl` = X ] ; then
  echo "ERROR: openssl command is not available."
  HAS_ERRORS=1
fi

if [ X`which dig` = X ] ; then
  echo "ERROR: dig command is not available."
  HAS_ERRORS=1
fi

if [ X`which keytool` = X ] ; then
  echo "ERROR: keytool command is not available."
  HAS_ERRORS=1
fi

if [ X`which aws` = X ] ; then
  echo "ERROR: aws command is not available."
  HAS_ERRORS=1
else
  /bin/echo -n "Testing aws route53 command... (zone: $R53ZONE)"
  aws route53 list-resource-record-sets --hosted-zone-id $R53ZONE | grep "\"Name\": \"$DOMAIN.\"" > /dev/null
  if [ $? != 0 ] ; then
    echo ""
    echo "ERROR: aws cli is too old or profile is not configure correctly."
    HAS_ERRORS=1
  else
    echo "ok."
  fi

  /bin/echo -n "Testing aws s3 command... (target: $KEYSTORE_LOCATION, action: read)"
  aws s3 ls $KEYSTORE_LOCATION > /dev/null
  if [ $? != 0 ] ; then
    echo ""
    echo "ERROR: aws cli is too old or profile is not configure correctly."
    HAS_ERRORS=1
  else
    echo "ok."
  fi
fi

if [ X$HAS_ERRORS != X ] ; then
  echo ""
  echo "-> Some errors are found."
  exit
fi

if [ ! -d $BASEDIR/dehydrated ] ; then
  echo "Installing dehydrated tool..."
  ( cd $BASEDIR ; git clone https://github.com/lukas2511/dehydrated.git )
  ( cd $BASEDIR/dehydrated ; git checkout v0.4.0 -q )
fi

echo "complete."
