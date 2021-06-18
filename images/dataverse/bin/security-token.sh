#!/usr/bin/env bash

. "${SCRIPT_DIR}/config"

echo "Protecting admin API with token"
export API_LOCAL="false"
api PUT 'admin/settings/:BlockedApiKey' -d "${API_KEY}"
api PUT 'admin/settings/:BlockedApiPolicy' -d 'unblock-key'
api PUT 'admin/settings/:BlockedApiEndpoints' -d 'admin,builtin-users'
echo
