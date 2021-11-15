#!/bin/bash
set -euo pipefail

# This script updates the <field> and <copyField> schema configuration necessary to properly
# index custom metadata fields in Solr.
# 1. Retrieve from Dataverse API endpoint
# 2. Parse and write Solr schema files (which might replace the included files)
# 3. Reload Solr
#
# List of variables:
# ${DATAVERSE_URL}: URL to Dataverse. Defaults to http://localhost:8080
# ${SOLR_URL}: URL to Solr. Defaults to http://localhost:8983
# ${UNBLOCK_KEY}: File path to secret or unblock key as string. Only necessary on k8s or when you secured your installation.
# ${TARGET}: Directory where to write the XML files. Defaults to /tmp
#
# Programs used (need to be available on your PATH):
# coreutils: mktemp, csplit
# curl

usage() {
  echo "usage: updateSchema.sh [options]"
  echo "options:"
  echo "    -d <url>      Dataverse URL, defaults to http://localhost:8080"
  echo "    -h            Show this help text"
  echo "    -s <url>      Solr URL, defaults to http://localhost:8983"
  echo "    -t <path>     Directory where to write the XML files. Defaults to /tmp"
  echo "    -u <key/file> Dataverse unblock key either as key string or path to keyfile"
}

### Init (with sane defaults)
DATAVERSE_URL=${DATAVERSE_URL:-"http://localhost:8080"}
SOLR_URL=${SOLR_URL:-"http://localhost:8983"}
TARGET=${TARGET:-"/tmp"}
UNBLOCK_KEY=${UNBLOCK_KEY:-""}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

# if cmdline args are given, override any env var setting (or defaults)
while getopts ":d:hs:t:u:" opt
do
   case $opt in
       d) DATAVERSE_URL=${OPTARG};;
       h) usage; exit 0;;
       s) SOLR_URL=${OPTARG};;
       t) TARGET=${OPTARG};;
       u) UNBLOCK_KEY=${OPTARG};;
       :) echo "Missing option argument for -${OPTARG}. Use -h for help." >&2; exit 1;;
      \?) echo "Unknown option -${OPTARG}." >&2; usage; exit 1;;
   esac
done

# Special handling of unblock key depending on referencing a secret file or key in var
if [ ! -z "${UNBLOCK_KEY}" ]; then
  if [ -f "${UNBLOCK_KEY}" ]; then
    UNBLOCK_KEY="?unblock-key=$(cat ${UNBLOCK_KEY})"
  else
    UNBLOCK_KEY="?unblock-key=${UNBLOCK_KEY}"
  fi
fi

# Call the new update-fields.sh script to update the schema
curl -f -s "${DATAVERSE_URL}/api/admin/index/solr/schema${UNBLOCK_KEY}" | ${SCRIPT_DIR}/update-fields.sh ${TARGET}/schema.xml

# Reload the Solr collection
echo "Triggering Solr RELOAD at ${SOLR_URL}/solr/admin/cores?action=RELOAD&core=collection1"
curl -f -sS "${SOLR_URL}/solr/admin/cores?action=RELOAD&core=collection1" >/dev/null
echo
