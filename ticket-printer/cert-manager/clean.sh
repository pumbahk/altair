#!/bin/bash

BASEDIR=$(cd $(dirname $0) && pwd)

(cd $BASEDIR ; rm -rf accounts certs dehydrated)
