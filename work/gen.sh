!/bin/bash

dst=`pwd`/box
if [ ! -d $dst ] ; then
    mkdir $dst
fi

css_suffix=2
genjson="python `pwd`/work/main.py ${css_suffix}"
genjson_booster="python `pwd`/work/booster_main.py ${css_suffix}"
($genjson ticketing/src/altair/app/ticketing/fc_auth > $dst/fc_auth.json)
($genjson_booster ticketing/src/altair/app/ticketing/booster > $dst/booster.json)
($genjson ticketing/src/altair/app/ticketing/orderreview > $dst/orderreview.json)
($genjson ticketing/src/altair/app/ticketing/cart > $dst/cart.json)

gensh="python `pwd`/work/replace.py"
gensh_booster="python `pwd`/work/booster_replace.py"
($gensh $dst/fc_auth.json > $dst/fc_auth.sh)
($gensh_booster $dst/booster.json > $dst/booster.sh)
## layout.static_url
($gensh $dst/orderreview.json > $dst/orderreview.sh)
($gensh $dst/cart.json > $dst/cart.sh)


bucket="tstar-dev/"
gen_upload_s3cmd_sh="python `pwd`/work/upload.py"
($gen_upload_s3cmd_sh $dst/fc_auth.json $bucket > $dst/s3_fc_auth.sh)
($gen_upload_s3cmd_sh $dst/booster.json $bucket > $dst/s3_booster.sh)
($gen_upload_s3cmd_sh $dst/orderreview.json $bucket > $dst/s3_orderreview.sh)
($gen_upload_s3cmd_sh $dst/cart.json $bucket > $dst/s3_cart.sh)
