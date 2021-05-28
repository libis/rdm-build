#!/usr/bin/env bash

. "${SCRIPT_DIR}/config"

echo "Restricting admin API to localhost only"
api PUT 'admin/settings/:BlockedApiPolicy' -d 'localhost-only'
api PUT 'admin/settings/:BlockedApiEndpoints' -d 'admin,builtin-users'
api DELETE 'admin/settings/:BlockedApiKey'
echo

export API_LOCAL="true"
