#!/bin/bash

set -e

NGBASEOPT="--base-href=/cart/spa/ --deploy-url=/cart/static/spa_cart/"
NGOPT="--aot=false --output-hashing=all --sourcemap=false --extract-css=true --environment=prod"

BRANCH=$(git symbolic-ref --short HEAD)

# for Mac
MD5="md5 -r"

if [ -x /usr/bin/md5sum ] ; then
  MD5=/usr/bin/md5sum
fi

/bin/echo -n "Checking node... "
node -v || exit 1

/bin/echo -n "Checking npm... "
npm -v || exit 1

WORKDIR=$(cd ../../ticketing/src/altair/app/ticketing/spa_cart && pwd)

echo "Calculating digest of source files..."
DIGEST=$(cd $WORKDIR && (ls package.json ; find src -type f | egrep -e "\.(ts|css|html|json|svg|ico|otf)$") | sort | xargs $MD5 | $MD5)
echo " -> $DIGEST"

if [ -e ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/version ] ; then
  BUILT_DIGEST=$(cat ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/version)
fi

if [ X$DIGEST == X$BUILT_DIGEST ] ; then
  echo ""
  echo "Source files are not changed after previous build process."
  echo "Remove ticketing/src/altair/app/ticketing/cart/static/spa_cart/version if force build needed."
  exit
fi

if [ -d $WORKDIR/node_modules ] ; then
  echo "Found node_modules directory."
  if [ X$BRANCH == Xdevelop ] ; then
    echo "Removing node_modules..."
    rm -rf $WORKDIR/node_modules
  fi
fi

DISTDIR=$WORKDIR/dist-$$
[ -e $DISTDIR ] && rm -rf $DISTDIR
mkdir -p $DISTDIR

echo "Running angular build process..."
(cd $WORKDIR && npm install && ./node_modules/.bin/ng build --output-path=$DISTDIR $NGBASEOPT $NGOPT)
echo "Completed"

echo "Injecting rollbar..."
for x in $DISTDIR/main.*.bundle.js
do
    (echo "" ; cat rollbar.js) >> $x
done

echo "Making gzip version scripts..."
for x in $DISTDIR/*.js
do
    cat $x | sed '/\/\/# sourceMappingURL=/d' | gzip > $x.gz
done

# install
echo "Installing files to ticketing/src/altair/app/ticketing/cart/..."
mkdir -p ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart
find ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/ -type f -delete
(cd $DISTDIR ; tar cf - --exclude index.html .) | (cd ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart ; tar xf -)
mkdir -p ../../ticketing/src/altair/app/ticketing/cart/templates/eagles/pc/spa_cart
cp $DISTDIR/index.html ../../ticketing/src/altair/app/ticketing/cart/templates/eagles/pc/spa_cart/

echo $DIGEST > ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/version

# remove workdir
echo "Removing working directory..."
rm -rf $DISTDIR

# commit
if [ X$BRANCH == Xdevelop ] ; then
    git add ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart -f -A
    git add ../../ticketing/src/altair/app/ticketing/cart/templates/eagles/pc/spa_cart/index.html
    git add ../../ticketing/src/altair/app/ticketing/cart/static/spa_cart/version
    git commit -m "rebuild spa_cart by script"
fi
