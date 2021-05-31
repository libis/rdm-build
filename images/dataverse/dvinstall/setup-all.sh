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
echo "      - API token: ${adminKey}"
api POST "admin/superuser/$(jq -r '.userName' $(data_file user-admin.json))"
echo

echo "Setting up the root Dataverse collection"
file="$(data_file dv-root.json)"
obj_single "dataverses" "$file" 'application/json' -H "X-Dataverse-key:${adminKey}"
alias="$(jq -r '.alias' "$file")"
api POST "dataverses/$alias/actions/:publish" -H "X-Dataverse-key:${adminKey}"
echo

echo "Setting up other Dataverse collections ..."
for f in "$(data_dir collections)"/*.json "$(custom_dir collections)"/*.json; do
  obj_single 'dataverses/${/0}' "$f" 'application/json' -H "X-Dataverse-key:${adminKey}"
  api POST "dataverses/$(jq -r '.alias' "$f")/actions/:publish" -H "X-Dataverse-key:${adminKey}"
done
echo

echo "Set the metadata blocks per collection ..."
obj_loop 'dataverses/${/0}/metadatablocks' collections/metadatablocks '*.json' 'application/json' -H "X-Dataverse-key:${adminKey}"
echo

echo "Set the default facets per collection ..."
obj_loop 'dataverses/${/0}/facets' collections/facets '*.json' 'application/json' -H "X-Dataverse-key:${adminKey}"
echo

echo "Setting up User groups per collection ..."
obj_loop 'dataverses/${/0}/groups' collections/groups '*.json' 'application/json' -H "X-Dataverse-key:${adminKey}"
echo

echo "Setting up assignments per collection ..."
obj_loop 'dataverses/${/0}/assignments' collections/assignments '*.json' 'application/json' -H "X-Dataverse-key:${adminKey}"

# Custom configuration
CUSTOMSCRIPT="${HOME_DIR}/custominstall/setup-all.sh"
[[ -e "${CUSTOMSCRIPT}" ]] && "${CUSTOMSCRIPT}" "${adminKey}"
