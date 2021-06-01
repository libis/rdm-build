#!/usr/bin/env bash

. ${HOME}/setup.sh

usage() {
  tput clear
  echo 'Menu'
  echo '===='
  echo '1. Export Datasets'
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
      read -n 1 -s -r -p "Press any key to continue"
      ;;
    *)
      ;;
  esac
  usage
  read -n 1 -p 'Choice: ' x
  echo
done