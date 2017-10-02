#!/bin/sh

source ./config

if [ X`which git` = X ] ; then
  echo "ERROR: git command is not available."
  exit
fi

if [ ! -d dehydrated ] ; then
  echo "Installing dehydrated tool..."
  git clone https://github.com/lukas2511/dehydrated.git
  ( cd dehydrated ; git checkout v0.4.0 -q )
fi

if [ X`which openssl` = X ] ; then
  echo "ERROR: openssl command is not available."
  exit
fi

if [ X`which aws` = X ] ; then
  echo "ERROR: aws command is not available."
  exit
fi

/bin/echo -n "Testing aws route53 command... "
aws route53 list-resource-record-sets --hosted-zone-id $R53ZONE | grep "\"Name\": \"$DOMAIN.\"" > /dev/null

if [ $? != 0 ] ; then
  echo ""
  echo "ERROR: aws cli is too old or profile is not configure correctly."
else
  echo "ok."
fi


/bin/echo -n "Testing aws s3 command..."
aws s3 ls s3://tstar/ticket-printer/keystore > /dev/null

if [ $? != 0 ] ; then
  echo ""
  echo "ERROR: aws cli is too old or profile is not configure correctly."
else
  echo "ok."
fi


if [ X`which dig` = X ] ; then
  echo "ERROR: dig command is not available."
fi

if [ X`which keytool` = X ] ; then
  echo "ERROR: keytool command is not available."
fi

echo "complete."
