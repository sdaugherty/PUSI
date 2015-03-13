#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: $0 <Region>"
	exit 1
fi

echo "Getting system list for ${1}"
wget -q -O- http://evemaps.dotlan.net/region/${1} | grep -e '/map/'${1} | cut -d '/' -f 4 | cut -d '"' -f 1 | sort -u > ${1}_sys

for i in `cat ${1}_sys`; do 
  echo "Parsing ${1}/${i}"
  wget -q -O- http://evemaps.dotlan.net/range/5/${i} | grep '/map' | cut -d ':' -f 2 | cut -d '"' -f 1 | sort -u | grep , | sed -e 's/,/","/g' | sed 's/^/["/;s/$/"]/' > ./systems/${i}.json
done;

find ./ -size 0 -print0 | xargs -0 rm
rm ${1}_sys
