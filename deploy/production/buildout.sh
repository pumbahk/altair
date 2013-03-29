#!/bin/sh

set -x

host_cfg=`hostname`.cfg

if [ -f $host_cfg ] ; then
    echo "Use $host_cfg"
    bin/buildout -c $host_cfg
else
    bin/buildout
fi
