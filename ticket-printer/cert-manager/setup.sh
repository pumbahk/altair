#!/bin/sh

if [ X`which git` = X ] ; then
  echo "ERROR: git command is not available."
  exit
fi

if [ ! -d dehydrated ] ; then
  git clone https://github.com/lukas2511/dehydrated.git
  ( cd dehydrated ; git checkout v0.4.0 -q )
fi

if [ X`which openssl` = X ] ; then
  echo "ERROR: openssl command is not available."
  exit
fi

if [ ! -r certs/localhost.altair-printer.tk/privkey.pem ] ; then
  mkdir -p certs/localhost.altair-printer.tk
  openssl pkcs12 -in ../src/main/resources/localhost.p12 -nocerts -nodes -password pass:secret -out certs/localhost.altair-printer.tk/privkey.pem
fi

if [ X`which dig` = X ] ; then
  echo "ERROR: dig command is not available."
fi
