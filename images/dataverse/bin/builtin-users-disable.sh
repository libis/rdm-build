#!/usr/bin/env bash

. "${SCRIPT_DIR}/config"

echo "Disabling Builtin Users API"
api DELETE 'admin/settings/BuiltinUsers.KEY'
echo