#!/bin/sh

./dehydrated/dehydrated -c -f ./config -t dns-01 --hook ./hook.sh \
-d localhost.altair-printer.tk
