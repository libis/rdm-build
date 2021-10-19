#!/usr/bin/env bash

. ${HOME}/setup.sh

usage() {
  tput clear
  echo 'Menu'
  echo '===='
  echo '1. Export Datasets'
  echo '2. Storage report'
  echo ''
  echo 'a. Capture metadata properties'
  echo 'b. Apply custom translations'
  echo ''
  echo '0. Exit'
}

x="$1"

while [ "$x" != "0" ]; do
  case "$x" in
    "0")
      exit
      ;;
    "1")
      ruby ${HOME}/export_datasets.rb
      ;;
    "2")
      ruby ${HOME}/storage_report.rb
      ;;
    "a")
      ruby ${HOME}/metadata_properties.rb /opt/dv_config/overwrite/metadatablocks /opt/languages
      ;;
    "b")
      ruby ${HOME}/customize_properties.rb /opt/dv_config/data/properties /opt/languages
      ;;
    *)
      ;;
  esac
  read -n 1 -s -r -p "Press any key to continue"
  usage
  read -n 1 -p 'Choice: ' x
  echo
done