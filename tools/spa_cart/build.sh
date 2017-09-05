#!/bin/sh

BRANCH=${1:-develop}
TMPDIR=altair-new-cart-$(date "+%Y%m%d%H%M%S")
NGOPT="--aot=false --output-hashing=all --sourcemap=false --extract-css=true --environment=prod"

git clone -b $BRANCH --depth 1 git@github.com:ticketstar/altair-new-cart.git $TMPDIR
REV=`(cd $TMPDIR ; git rev-parse HEAD)`

cd $TMPDIR
npm update
ng build --base-href=/cart/spa/ --deploy-url=/cart/static/spa_cart/ $NGOPT
sed -i "" '/\/\/# sourceMappingURL=/d' dist/*.js
for x in dist/*.js
do
		gzip -c $x > $x.gz
done
cd ..

if [ -d ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart ] ; then
    git rm ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/*
fi

cp -r $TMPDIR/dist ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart
rm ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/index.html
cp $TMPDIR/dist/index.html ../../ticketing/src/altair/app/ticketing/cart/templates/eagles/pc/spa_cart/

git add ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart -f
git add ../../ticketing/src/altair/app/ticketing/cart/templates/eagles/pc/spa_cart/index.html

git commit -m "merge new-cart $REV by script"
