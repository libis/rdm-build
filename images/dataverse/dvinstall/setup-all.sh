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
datafiles_loop 'admin/datasetfield/load' metadatablocks '*.tsv' 'text/tab-separated-values'
echo

echo "Setup the builtin roles ..."
datafiles_loop 'admin/roles' roles
echo

echo "Setup the authentication providers"
datafiles_loop 'admin/authenticationProviders/' authentication-providers
echo

echo "Application settings update ..."
settings_loop 'admin/settings' settings
echo

echo "Setting up the admin user (and as superuser)"
datafile "builtin-users?password=${ADMIN_PASSWORD}&key=${API_USERSKEY}" "$(data_file user-admin.json)"
adminKey="$(echo "${REPLY}" | jq .data.apiToken | tr -d \")"
echo "      - API token: $(echo ${adminKey} | tee "${DOMAIN_DIR}/.adminKey")" 
api POST "admin/superuser/$(jq -r '.userName' $(data_file user-admin.json))"
echo

echo "Setting up other builtin users"
datafiles_loop "builtin-users?password=${USER_PASSWORD}&key=${API_USERSKEY}" users
echo

echo "Setting up the root Dataverse collection"
file="$(data_file dv-root.json)"
superAdmin datafile "dataverses" "$file"
alias="$(jq -r '.alias' "$file")"
superAdmin api POST "dataverses/$alias/actions/:publish"
echo

echo "Setting up other Dataverse collections ..."
for f in "$(data_dir collections)"/*.json "$(custom_dir collections)"/*.json; do
  superAdmin datafile 'dataverses/${/0}' "$f"
  superAdmin api POST "dataverses/$(jq -r '.alias' "$f")/actions/:publish"
done
echo

echo "Set the metadata blocks per collection ..."
superAdmin datafiles_loop 'dataverses/${/0}/metadatablocks' collections/metadatablocks
echo

echo "Set the default facets per collection ..."
superAdmin datafiles_loop 'dataverses/${/0}/facets' collections/facets
echo

echo "Setting up User groups per collection ..."
superAdmin datafiles_loop 'dataverses/${/0}/groups' collections/groups
echo

echo "Setting up group assignments per collection ..."
superAdmin datafiles_loop 'dataverses/${/0}/groups/${/1}/roleAssignees' collections/group-assignments
echo

echo "Setting up role assignments per collection ..."
superAdmin datafiles_loop 'dataverses/${/0}/assignments' collections/role-assignments
echo

echo "Configuring external tools ..."
superAdmin datafiles_loop 'admin/externalTools' external-tools

# Custom configuration
CUSTOMSCRIPT="${CUSTOM_INSTALL}/setup-all.sh"
[[ -e "${CUSTOMSCRIPT}" ]] && "${CUSTOMSCRIPT}" "${adminKey}"
