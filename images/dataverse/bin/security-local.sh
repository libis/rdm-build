#!/usr/bin/env bash

. "${SCRIPT_DIR}/config"

echo "Restricting admin API to localhost only"
api DELETE 'admin/settings/:BlockedApiKey'
api PUT 'admin/settings/:BlockedApiPolicy' -d 'localhost-only'
api PUT  'admin/settings/:BlockedApiEndpoints' -d 'admin,builtin-users'
echo

export API_LOCKED=0
