#!/usr/bin/env bash

. "${SCRIPT_DIR}/config"

echo "Protecting admin API with token"
api PUT 'admin/settings/:BlockedApiKey' -d "${API_KEY}"
api PUT 'admin/settings/:BlockedApiPolicy' -d 'unblock-key'
api PUT 'admin/settings/:BlockedApiEndpoints' -d 'admin,builtin-users'
echo

export API_LOCKED=1
