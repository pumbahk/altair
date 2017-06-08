#!/bin/sh

if [ `git status | head -1 | grep detached | wc -l` = 0 ] ; then
		git checkout `git rev-parse HEAD`
fi

if [ -d ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart ] ; then
		echo "please remove ticketing/src/altair/app/ticketing/cart/static/spa_cart/ before use this script."
		exit
fi

if [ -d ./altair-new-cart-x ] ; then
		echo "please remove working directory: altair-new-cart-x/"
		exit
fi

git clone -b develop --depth 1 git@github.com:ticketstar/altair-new-cart.git altair-new-cart-x
REV=`(cd altair-new-cart-x ; git rev-parse HEAD)`

if [ -d ./altair-new-cart-$REV ] ; then
		echo "found same revision. please remove: altair-new-cart-$REV/"
		rm -rf altair-new-cart-x
		exit
fi

mv altair-new-cart-x altair-new-cart-$REV

cd altair-new-cart-$REV
npm update
ng build --base-href=/cart/spa/ --deploy-url=/cart/static/spa_cart/
for x in dist/*.js
do
		gzip -c $x > $x.gz
done
cp -r dist ../../../ticketing/src/altair/app/ticketing/cart/static/spa_cart
cd ..

git add ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart -f

git commit -m "temporary added: built spa $REV"

echo "completed. you can push it by following command:"
echo "  git push origin HEAD:feature/new-cart-qa -f"
