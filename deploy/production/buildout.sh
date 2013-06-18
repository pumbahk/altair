#!/bin/bash

role=
suffix=
rolemap="$(dirname $0)/rolemap"

while [ $# -ge 1 ]; do
    case $1 in
        -s|--suffix)
            shift
            suffix=".$1"
            ;;
        -*)
            echo "Invalid option: $1" >&2
            exit 255
            ;;
        *)
            role=$1
            ;;
    esac
    shift
done

if [ -z "$role" ]; then
    hostname=$(hostname)
    role=$(grep "^${hostname}\s" "${rolemap}" | cut -f 2)
fi

role_cfg="${role}${suffix}.cfg"
default_cfg="buildout${suffix}.cfg"

if [ -f $role_cfg ] ; then
    cfg="$role_cfg"
else
    echo "Configuration missing: ${role_cfg}" >&2
    exit 1
fi
echo "Using [33m${cfg}[0m"
if tty >/dev/null; then
    echo "Press enter to continue, ^C to abort"
    read
fi
bin/buildout -c ${cfg} deploy:root="/srv/altair${suffix}"
