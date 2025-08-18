#!/bin/bash

dirLocal=$(pwd)

# Set some defaults as documented
VERSIONS=${VERSIONS:-"v1.5"}

echo "Using Provider Url=${PREVIEWERS_PROVIDER_URL} for versions ${VERSIONS}"
cd /app
# Split VERSIONS on commas and/or spaces and iterate
# Accepts values like: "v1.3,v1.4" or "v1.3 v1.4" or mixed
versions="${VERSIONS//,/ }"
for ver in $versions; do
    # trim surrounding whitespace
    ver="$(echo "$ver" | xargs)"
    [ -z "$ver" ] && continue
    echo "Installing previewers/${ver} from ${PREVIEWERS_PROVIDER_URL}"
    ./localinstall.sh "previewers/${ver}" "${PREVIEWERS_PROVIDER_URL}"
    # copy any markdown files into the version folder if present (ignore errors)
    cp -- *.md "previewers/${ver}" 2>/dev/null || true
    # ensure the target previewers directory exists and copy only this version to the webroot
    mkdir -p /usr/share/nginx/html/previewers
    cp -r "previewers/${ver}" "/usr/share/nginx/html/previewers/${ver}" 2>/dev/null || true
done

