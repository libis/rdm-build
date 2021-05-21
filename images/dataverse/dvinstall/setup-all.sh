#!/usr/bin/env bash

. ${SCRIPT_DIR}/config
. ${DVINSTALL_DIR}/setup-tools

command -v jq &>/dev/null || { echo >&2 '`jq` ("sed for JSON") is required, but not installed. Aborting.'; exit 1; }

echo "Deleting all data from Solr"
curl -sS -f "${SOLR_URL}/solr/collection1/update/json?commit=true" \
    -H "Content-type: application/json" -X POST -d "{\"delete\": { \"query\":\"*:*\"}}" >/dev/null
echo

echo "Setting up the metadata blocks"
api GET 'admin/datasetfield/loadNAControlledVocabularyValue'
obj_loop 'admin/datasetfield/load' metadatablocks '*.tsv' 'text/tab-separated-values'
echo

echo "Setup the builtin roles ..."
obj_loop 'admin/roles' roles
echo

echo "Setup the authentication providers"
obj_loop 'admin/authenticationProviders/' authentication-providers
echo

echo "Application settings update ..."
settings_loop 'admin/settings' settings
echo

echo "Setting up the admin user (and as superuser)"
obj_single "builtin-users?password=${ADMIN_PASSWORD}&key=${API_USERSKEY}" "$(data_file user-admin.json)"
adminKey="$(echo "${REPLY}" | jq .data.apiToken | tr -d \")"
api POST 'admin/superuser/dataverseAdmin'
echo

echo "Setting up the root Dataverse collection"
obj_single "dataverses/?key=${adminKey}" "$(data_file dv-root.json)"
echo

echo "Set the metadata blocks for Root"
api POST "dataverses/:root/metadatablocks/?key=${adminKey}" -H 'Content-type:application/json' -d "[\"citation\"]"
echo

echo "Set the default facets for Root"
api POST "dataverses/:root/facets/?key=${adminKey}" -H 'Content-type:application/json' -d "[\"authorName\",\"subject\",\"keywordValue\",\"dateOfDeposit\"]"
echo

echo "Setting up other Dataverse collections ..."
obj_loop "dataverses/\${/}?key=${adminKey}" collections
echo

# Custom configuration
CUSTOMSCRIPT="${HOME_DIR}/custominstall/setup-all.sh"
[[ -e "${CUSTOMSCRIPT}" ]] && "${CUSTOMSCRIPT}" "${adminKey}"
