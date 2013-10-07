#!/bin/bash

suffix=

if [ $# -ge 1 ]; then
    suffix=".$1"
else
    suffix=".local"
fi

host_cfg="$(hostname).cfg"
default_cfg="buildout${suffix}.cfg"

if [ -f $host_cfg ] ; then
    cfg="$host_cfg"
else
    cfg="$default_cfg"
fi

echo "Using [33m${cfg}[0m"
if tty >/dev/null; then
    echo "Press enter to continue, ^C to abort"
    read
fi
bin/buildout -c ${cfg} deploy:root="/srv/altair${suffix}"
