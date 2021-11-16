#!/usr/bin/env bash

################################################################################
# Add Dataverse app to deploy dir when not yet deployed.
#
# It is necessary to do this before the init_1 script starts as it will perform
# the deployment for any app in the deploy dir.
################################################################################

# Include some sane defaults
. "${SCRIPT_DIR}/default.config"

# Add Dataverse app to deploy dir
if test -d "${DOMAIN_DIR}/applications/dataverse"
then
  echo "Dataverse already deployed"
  # Redeploy extra files, just to be sure
  "${SCRIPT_DIR}/deploy.sh"
else
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
      cat "${SECRETS_DIR}/$alias/password" | sed -e "s#^#AS_ADMIN_ALIASPASSWORD=#" > /tmp/.${alias}_asadmin
      echo "create-password-alias ${alias}_password_alias --passwordfile /tmp/.${alias}_asadmin" >> "${DV_POSTBOOT}"
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
  echo "create-jdbc-connection-pool --restype=javax.sql.DataSource --datasourceclassname=org.postgresql.ds.PGPoolingDataSource --property=create=true:User=${POSTGRES_USER}:PortNumber=${POSTGRES_PORT}:databaseName=${POSTGRES_DATABASE}:ServerName=${POSTGRES_SERVER} dvnDbPool" >> "${DV_POSTBOOT}"
  echo 'set resources.jdbc-connection-pool.dvnDbPool.property.password=${ALIAS=db_password_alias}' >> "${DV_POSTBOOT}"
  echo "create-jdbc-resource --connectionpoolid=dvnDbPool jdbc/VDCNetDS" >> "${DV_POSTBOOT}"

  echo "  - JavaMail."
  echo "create-javamail-resource --mailhost=${MAIL_SERVER} --mailuser=${MAIL_FROMADDRESS} --fromaddress=${MAIL_FROMADDRESS} mail/notifyMailSession" >> "${DV_POSTBOOT}"

  #echo "  - EJB Timer."
  #echo "create-jvm-options '-Ddataverse.timerServer=true'" >> ${DV_POSTBOOT}

  echo "  - AJP connector"
  echo "create-network-listener --protocol=http-listener-1 --listenerport=8009 --jkenabled=true jk-connector" >> "${DV_POSTBOOT}"

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

  # Deploy Dataverse war file
  ###########################
  echo "Deploying Dataverse application"
  echo "deploy ${DVINSTALL_DIR}/dataverse.war" >> "${DV_POSTBOOT}"

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

fi
