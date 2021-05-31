#!/usr/bin/env bash
[[ -f /run/secrets/api/adminKey ]] && export API_TOKEN="$(cat /run/secrets/api/adminKey)"
export API_URL="http://${DATAVERSE_SERVICE_HOST}:${DATAVERSE_SERVICE_PORT_HTTP}/api/v1"
echo "API environment initialized:"
echo "  API_URL: ${API_URL}"
echo "  API_TOKEN: ${API_TOKEN"
