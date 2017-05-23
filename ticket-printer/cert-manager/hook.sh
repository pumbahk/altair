#!/bin/sh

COMMAND=$1
DOMAIN=$2
TOKEN=$4

check () {
  while true
  do
    LINE=`dig txt _acme-challenge.$DOMAIN +trace +short | grep ^TXT`
    TXT=`echo $LINE | sed 's/^.*"\(.*\)".*\$/\1/'`
    if [ "X$TXT" = "X$TOKEN" ] ; then
      echo "confirmed."
      return
    fi

    echo "$LINE"
    echo "cannot confirm, hit enter key after set up"
    read X
  done
}

if [ "X$COMMAND" = "Xdeploy_challenge" ] ; then
  echo "create dns record:"
  echo "  _acme-challenge.$DOMAIN TXT $TOKEN"
  echo ""
  echo "hit enter key after set up"
  read X
  check
fi
