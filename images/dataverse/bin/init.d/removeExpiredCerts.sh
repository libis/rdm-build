#!/bin/bash

# remove expired certs from a keystore
# set FN to the keystore file

if [[ -d ${DOMAIN_DIR}/config ]]
then

pushd ${DOMAIN_DIR}/config

FN=cacerts.jks

echo "finding expired certs..."
ALIASES=`keytool -list -v -keystore $FN -storepass changeit | grep -i 'alias\|until' `

echo "$ALIASES" > aliases.txt

i=1
# Split dates and aliases to different arrays
while read p; do
    if ! ((i % 2)); then
        arr_date+=("$p")
    else
        arr_cn+=("$p")
    fi
    i=$((i+1))
done < aliases.txt
i=0

# Parse until-dates ->
# convert until-dates to "seconds from 01-01-1970"-format -> 
# compare until-dates with today-date -> 
# delete expired aliases
for date_idx in $(seq 0 $((${#arr_date[*]}-1)));
do
    a_date=`echo ${arr_date[$date_idx]} | awk -F"until: " '{print $2}'`
    if [ `date +%s --date="$a_date"` -lt `date +%s` ];
    then
        echo "removing ${arr_cn[$i]} expired: $a_date"
        alias_name=`echo "${arr_cn[$i]}" | awk -F"name: " '{print $2}'`
        keytool -delete -alias "$alias_name" -keystore $FN -storepass changeit
    fi
    i=$((i+1))
done
echo "Done."

popd

fi