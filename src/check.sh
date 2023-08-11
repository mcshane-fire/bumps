#!/bin/bash

for i in ../git/bumps-results/results/ad_format/*.txt; do
    F=`echo $i | sed -e  's#w\.txt#_women.txt#' -e 's#m\.txt#_men.txt#' -e 's#ad_format#tg_format#' -e 's#format/t\([0-9]\)#format/torpids\1#' -e 's#format/l#format/lents#' -e 's#format/m#format/mays#' -e 's#format/e#format/eights#'`

    if [ -e $F ]; then
        echo $i $F
        ./convert.py -ad $i t
        diff t $F
    fi
    
done
