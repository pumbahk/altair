#!/bin/sh

BRANCH=${1:-develop}
TMPDIR=altair-new-cart-$(date "+%Y%m%d%H%M%S")
NGOPT="--aot=false --output-hashing=all --sourcemap=false --extract-css=true --environment=prod"

/bin/echo -n "Checking node... "
node -v || exit 1

/bin/echo -n "Checking npm... "
npm -v || exit 1

git clone -b $BRANCH --depth 1 git@github.com:ticketstar/altair-new-cart.git $TMPDIR
if [ ! -d $TMPDIR ] ; then
		echo "git failed."
		exit 1
fi

REV=`(cd $TMPDIR ; git rev-parse HEAD)`

cd $TMPDIR
npm update
./node_modules/.bin/ng build --base-href=/cart/spa/ --deploy-url=/cart/static/spa_cart/ $NGOPT

(echo "" ; cat ../rollbar.js) >> $(ls dist/main.*.bundle.js)

for x in dist/*.js
do
		cat $x | sed '/\/\/# sourceMappingURL=/d' | gzip > $x.gz
done
cd ..

mkdir -p ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart
find ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/ -type f -delete
cp -r $(ls $TMPDIR/dist | grep -v index.html) ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/
cp $TMPDIR/dist/index.html ../../ticketing/src/altair/app/ticketing/cart/templates/eagles/pc/spa_cart/

git add ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart -f -A
git add ../../ticketing/src/altair/app/ticketing/cart/templates/eagles/pc/spa_cart/index.html
git commit -m "merge new-cart $REV by script"
