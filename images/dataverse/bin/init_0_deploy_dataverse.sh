#!/usr/bin/env bash

################################################################################
# Add Dataverse app to deploy dir when not yet deployed.
#
# It is necessary to do this before the init_1 script starts as it will perform
# the deployment for any app in the deploy dir.
################################################################################

# Include some sane defaults
. "${SCRIPT_DIR}/default.config"

# fail on any error
set -e

# Define postboot commands file to be read by Payara and clear it
DV_PREBOOT="${PAYARA_DIR}/dataverse_preboot"
DV_POSTBOOT="${PAYARA_DIR}/dataverse_postboot"

echo "# Dataverse preboot configuration for Payara" > "${DV_PREBOOT}"
echo "# Dataverse postboot configuration for Payara" > "${DV_POSTBOOT}"

echo "Configuring domain ..."

# Password aliases from secrets
###############################

echo '  - password aliases'
# TODO: This is ugly and dirty. It leaves leftovers on the filesystem.
#       It should be replaced by using proper config mechanisms sooner than later,
#       like MicroProfile Config API.
for alias in rserve doi db
do
  if [ -f "${SECRETS_DIR}/$alias/password" ]; then
    cat "${SECRETS_DIR}/$alias/password" | sed -e "s#^#AS_ADMIN_ALIASPASSWORD=#" > ${SECRETS_DIR}/${alias}/.asadmin
    echo "create-password-alias ${alias}_password_alias --passwordfile ${SECRETS_DIR}/${alias}/.asadmin" >> "${DV_POSTBOOT}"
  else
    echo "WARNING: Could not find 'password' secret for ${alias} in ${SECRETS_DIR}. Check your Secrets and their mounting!"
  fi
done

# Setup OpenAPI 
###############

echo '  - OpenAPI setup'
echo "set-openapi-configuration --enabled=true --corsheaders=true" >> "${DV_PREBOOT}"
echo "set-config-property --propertyName mp.openapi.servers --propertyValue ${dataverse_siteUrl} --source domain" >> "${DV_POSTBOOT}"

# Create AWS access credentials when storage driver is set to s3
################################################################

# Find all access keys
if [ -d "${SECRETS_DIR}/s3" ]; then
  S3_KEYS=`find "${SECRETS_DIR}/s3" -readable -type f -iname '*access-key'`
  S3_CRED_FILE="${HOME_DIR}/.aws/credentials"
  mkdir -p `dirname "${S3_CRED_FILE}"`
  rm -f ${S3_CRED_FILE}
  # Iterate keys
  while IFS= read -r S3_ACCESS_KEY; do
    echo "  - Loading S3 key ${S3_ACCESS_KEY}"
    # Try to find the secret key, parse for profile and add to the credentials file.
    S3_PROFILE=`echo "${S3_ACCESS_KEY}" | sed -ne "s#.*/\(.*\)-access-key#\1#p"`
    S3_SECRET_KEY=`echo "${S3_ACCESS_KEY}" | sed -ne "s#\(.*/\|.*/.*-\)access-key#\1secret-key#p"`

    if [ -r "${S3_SECRET_KEY}" ]; then
      [ -z "${S3_PROFILE}" ] && echo "[default]" >> "${S3_CRED_FILE}" || echo "[${S3_PROFILE}]" >> "${S3_CRED_FILE}"
      cat "${S3_ACCESS_KEY}" | sed -e "s#^#aws_access_key_id = #" -e "s#\$#\n#" >> "${S3_CRED_FILE}"
      cat "${S3_SECRET_KEY}" | sed -e "s#^#aws_secret_access_key = #" -e "s#\$#\n#" >> "${S3_CRED_FILE}"
      echo "" >> "${S3_CRED_FILE}"
    else
      echo "ERROR: Could not find or read matching \"$S3_SECRET_KEY\"."
      exit 1
    fi
  done <<< "${S3_KEYS}"
fi

# Domain-spaced resources (JDBC, JMS, ...)
##########################################

# TODO: This is ugly and dirty. It should be replaced with resources from
#       EE 8 code annotations or at least glassfish-resources.xml
# NOTE: postboot commands is not multi-line capable, thus spaghetti needed.

echo '  - JMS resources'
cat >> "${DV_POSTBOOT}" << 'EOF'
delete-connector-connection-pool --cascade=true jms/__defaultConnectionFactory-Connection-Pool
create-connector-connection-pool --steadypoolsize=1 --maxpoolsize=250 --poolresize=2 --maxwait=60000 --raname=jmsra --connectiondefinition=javax.jms.QueueConnectionFactory jms/IngestQueueConnectionFactoryPool
create-connector-resource --poolname=jms/IngestQueueConnectionFactoryPool jms/IngestQueueConnectionFactory
create-admin-object --restype=javax.jms.Queue --raname=jmsra --property=Name=DataverseIngest jms/DataverseIngest
EOF

echo "  - JDBC resources."
echo "create-system-properties dataverse.db.user=${POSTGRES_USER}" >> "${DV_POSTBOOT}"
echo "create-system-properties dataverse.db.host=${POSTGRES_SERVER}" >> "${DV_POSTBOOT}"
echo "create-system-properties dataverse.db.port=${POSTGRES_PORT}" >> "${DV_POSTBOOT}"
echo "create-system-properties dataverse.db.name=${POSTGRES_DATABASE}" >> "${DV_POSTBOOT}"

# if [ -f "${SECRETS_DIR}/db/password" ]; then
#   cat "${SECRETS_DIR}/db/password" | sed -e "s#^#AS_ADMIN_ALIASPASSWORD=#" > ${SECRETS_DIR}/db/.asadmin
#   echo "create-password-alias dataverse.db.password --passwordfile ${SECRETS_DIR}/db/.asadmin" >> "${DV_POSTBOOT}"
# else
#   echo "WARNING: Could not find 'password' secret for database."
# fi

echo "  - JavaMail."
echo "delete-javamail-resource mail/notifyMailSession" >> "${DV_POSTBOOT}"
echo "create-javamail-resource --mailhost ${MAIL_SERVER} --mailuser ${MAIL_FROMADDRESS} --fromaddress=${MAIL_FROMADDRESS} mail/notifyMailSession" >> "${DV_POSTBOOT}"

echo "  - EJB Timer."
# echo "create-jvm-options '-Ddataverse.timerServer=true'" >> ${DV_POSTBOOT}
# echo "set configs.config.server-config.ejb-container.ejb-timer-service.timer-datasource=jdbc/VDCNetDS" >> ${DV_POSTBOOT}

echo "  - AJP connector"
echo "create-network-listener --protocol http-listener-1 --listenerport 8009 --jkenabled true jk-connector" >> "${DV_POSTBOOT}"

# Disable logging for grizzly SSL problems -- commented out as this is not GF 4.1
# echo "set-log-levels org.glassfish.grizzly.http.server.util.RequestUtils=SEVERE" >> ${DV_POSTBOOT}

echo "  - COMET support"
echo "set server-config.network-config.protocols.protocol.http-listener-1.http.comet-support-enabled=true" >> "${DV_POSTBOOT}"

echo "  - SAX parser"
echo "create-system-properties javax.xml.parsers.SAXParserFactory=com.sun.org.apache.xerces.internal.jaxp.SAXParserFactoryImpl" >> ${DV_POSTBOOT}

echo "  - network timeout"
echo "set server-config.network-config.protocols.protocol.http-listener-1.http.request-timeout-seconds=3600" >> ${DV_POSTBOOT}

# Domain based configuration options
####################################

# Set Dataverse environment variables
echo "  - system properties"
#env | grep -Ee "^(dataverse|doi)_" | sort -fd
env -0 | grep -z -Ee "^(dataverse|doi)_" | while IFS='=' read -r -d '' k v
do
  # transform __ to -
  KEY=`echo "${k}" | sed -e "s#__#-#g"`

  # transform remaining single _ to .
  KEY=`echo "${KEY}" | tr '_' '.'`

  # escape colons in values
  v=`echo "${v}" | sed -e 's/:/\\\:/g'`

  echo "create-system-properties ${KEY}=${v}" >> "${DV_POSTBOOT}"
done

# Production performance configuration
######################################
echo "Performance settings ..."

echo "  - no development options"
echo "set configs.config.server-config.admin-service.das-config.dynamic-reload-enabled=false" >> "${DV_POSTBOOT}"
echo "set configs.config.server-config.admin-service.das-config.autodeploy-enabled=false" >> "${DV_POSTBOOT}"

echo "  - disable jsp dynamic reloading"
sed -i 's#<servlet-class>org.apache.jasper.servlet.JspServlet</servlet-class>#<servlet-class>org.apache.jasper.servlet.JspServlet</servlet-class>\n    <init-param>\n      <param-name>development</param-name>\n      <param-value>false</param-value>\n    </init-param>\n    <init-param>\n      <param-name>genStrAsCharArray</param-name>\n      <param-value>true</param-value>\n    </init-param>#' ${DOMAIN_DIR}/config/default-web.xml

echo "  - disable https listener"
echo "set configs.config.server-config.network-config.network-listeners.network-listener.http-listener-2.enabled=false" >> "${DV_POSTBOOT}"

# Run custom commands, if available
###################################
[ -f "${HOME_DIR}/custominstall/preboot" ] && cat "${HOME_DIR}/custominstall/preboot" >> "${DV_PREBOOT}"
[ -f "${HOME_DIR}/custominstall/postboot" ] && cat "${HOME_DIR}/custominstall/postboot" >> "${DV_POSTBOOT}"

# Add the commands to the existing preboot file
###############################################
echo "$(cat ${DV_PREBOOT})" >> "${PREBOOT_COMMANDS}"
echo "preboot contains the following commands:"
echo "--------------------------------------------------"
cat "${PREBOOT_COMMANDS}"
echo "--------------------------------------------------"

# Add the commands to the existing postboot file
################################################
echo "$(cat ${DV_POSTBOOT})" >> "${POSTBOOT_COMMANDS}"
echo "postboot contains the following commands:"
echo "--------------------------------------------------"
cat "${POSTBOOT_COMMANDS}"
echo "--------------------------------------------------"

echo "Configuring jHove"
cp "${DVINSTALL_DIR}/jhove"* "${DOMAIN_DIR}/config/"
sed -i "${DOMAIN_DIR}/config/jhove.conf" -e "s#file://.*/jhoveConfig\.xsd#file://${DOMAIN_DIR}/config/jhoveConfig.xsd#g"
