#!/usr/bin/env bash

# Load configuration
. "${SCRIPT_DIR}/config"

echo "Clearing index timestamps"
api DELETE "admin/index/timestamps"
echo

echo "Starting async reindexing"
api GET "admin/index/continue"
echo
