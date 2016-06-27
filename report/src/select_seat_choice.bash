#!/bin/bash
# Run against ticketing.cart log
# Output seat choice log data loadable to order_select table

zgrep -F -e 'seat selected by user' -e 'selecting seat by system' $1 \
    | grep -F eagles | sed 's/.*,"message":"\([^"]\+\)".*/\1/' | awk 'BEGIN{OFS="\t"}{print $1 " " $2, $3, $10}' | tr , . \
    > order_select.${1//\//_}.out