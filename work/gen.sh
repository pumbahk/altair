#!/bin/bash

dst=`pwd`/box
if [ ! -d $dst ] ; then
    mkdir $dst
fi

genjson="python `pwd`/work/main.py"
($genjson ticketing/src/altair/app/ticketing/fc_auth > $dst/fc_auth.json)
($genjson ticketing/src/altair/app/ticketing/orderreview > $dst/orderreview.json)
($genjson ticketing/src/altair/app/ticketing/cart > $dst/cart.json)

bucket="tstar/"
gen_upload_s3cmd_sh="python `pwd`/work/upload.py"
($gen_upload_s3cmd_sh $dst/fc_auth.json $bucket > $dst/s3_fc_auth.sh)
($gen_upload_s3cmd_sh $dst/orderreview.json $bucket > $dst/s3_orderreview.sh)
($gen_upload_s3cmd_sh $dst/cart.json $bucket > $dst/s3_cart.sh)

gensh="python `pwd`/work/replace.py"
($gensh $dst/fc_auth.json > $dst/fc_auth.sh)
($gensh $dst/orderreview.json > $dst/orderreview.sh)
($gensh $dst/cart.json > $dst/cart.sh)

