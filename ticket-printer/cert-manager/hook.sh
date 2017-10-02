#!/bin/bash

COMMAND=$1
# DOMAIN_=$2

source ./config

check () {
  while true
  do
    LINE=`dig txt _acme-challenge.$DOMAIN +trace +short | grep ^TXT`
    echo "$LINE"
    TXT=`echo $LINE | sed 's/^.*"\(.*\)".*\$/\1/'`
    if [ "X$TXT" = "X$TOKEN" ] ; then
      echo "confirmed."
      return
    fi

    sleep 3
  done
}

if [ "X$COMMAND" = "Xdeploy_challenge" ] ; then
  TOKEN=$4
  echo "Updating TXT records for Zone: $R53ZONE..."
  cat update-txt.template.json | \
    sed "s/{{DOMAIN}}/$DOMAIN/" |  \
    sed "s/{{TOKEN}}/$TOKEN/" > update-txt.json
  aws route53 change-resource-record-sets --hosted-zone-id "$R53ZONE" --change-batch file://update-txt.json
  rm update-txt.json

  check
fi

if [ "X$COMMAND" = "Xdeploy_cert" ] ; then
  CERT=$4
  FULL=$5
  CHAIN=$6
  echo "new certificates are generated."
  [ -f $DEST ] && rm $DEST
  keytool -importcert -keystore $DEST -storepass $KEYSTORE_PASSWORD -storetype JKS -noprompt -alias 0 -file $CERT
  keytool -importcert -keystore $DEST -storepass $KEYSTORE_PASSWORD -storetype JKS -noprompt -alias 1 -file $CHAIN
  echo "keystore is generated."
fi
