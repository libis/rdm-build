#!/usr/bin/env bash
export PATH=${HOME}:${HOME}/scripts:${PATH}
[[ -f /opt/domain/.adminKey ]] && API_TOKEN="$(cat /opt/domain/.adminKey)"
API_URL="http://${DATAVERSE_SERVICE_HOST}:${DATAVERSE_SERVICE_PORT_HTTP}/api/v1"
echo "API environment initialized:"
echo "  API_URL: ${API_URL}"
echo "  API_TOKEN: ${API_TOKEN}"
export API_URL
export API_TOKEN
export DATA_DIR="/opt/data"