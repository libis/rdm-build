#!/bin/bash

dirLocal=$(pwd)

# Set some defaults as documented
VERSIONS=${VERSIONS:-"v1.5"}

echo "Using Provider Url=${PREVIEWERS_PROVIDER_URL} for versions ${VERSIONS}"
cd /app
if echo "$VERSIONS" | grep -q "\bv1.3\b"; then
    ./localinstall.sh previewers/v1.3 ${PREVIEWERS_PROVIDER_URL}
    cp *.md previewers/v1.3
fi
if echo "$VERSIONS" | grep -q "\bv1.4\b"; then
    ./localinstall.sh previewers/v1.4 ${PREVIEWERS_PROVIDER_URL}
    cp *.md previewers/v1.4
fi
if echo "$VERSIONS" | grep -q "\bv1.5\b"; then
    ./localinstall.sh previewers/v1.5 ${PREVIEWERS_PROVIDER_URL}
    cp *.md previewers/v1.5
fi
if echo "$VERSIONS" | grep -q "\bbetatest\b"; then
    ./localinstall.sh previewers/betatest ${PREVIEWERS_PROVIDER_URL}
    cp *.md previewers/betatest    
fi

cp -r ./previewers /usr/share/nginx/html
