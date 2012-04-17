#!/bin/sh
if [ x"$VIRTUAL_ENV" == x ] ; then
    echo "maybe you forget to use virtualenv!"
    exit 1
fi
python setup.py dev
alembic upgrade head
