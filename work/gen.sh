#!/bin/bash

dst=`pwd`/box
if [ ! -d $dst ] ; then
    mkdir $dst
fi

genjson="python `pwd`/work/main.py"
($genjson ticketing/src/altair/app/ticketing/fc_auth > $dst/fc_auth.json)
($genjson ticketing/src/altair/app/ticketing/orderreview > $dst/orderreview.json)
($genjson ticketing/src/altair/app/ticketing/cart > $dst/cart.json)

gensh="python `pwd`/work/replace.py"
($gensh $dst/fc_auth.json > $dst/fc_auth.sh)
($gensh $dst/orderreview.json > $dst/orderreview.sh)
($gensh $dst/cart.json > $dst/cart.sh)

