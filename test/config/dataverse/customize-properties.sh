#!/usr/bin/env bash

# Load configuration
. "${SCRIPT_DIR}/config"
. ${DVINSTALL_DIR}/setup-tools

echo "Properties files ..."

# Copy properties files
echo "  - copying source files"
PROP_DIR="/languages"
mkdir -p "${PROP_DIR}"

# ## Copy only Bundle.properties
cp "${DOMAIN_DIR}/applications/dataverse/WEB-INF/classes/propertyFiles/Bundle.properties" "${PROP_DIR}"
# ## Copy all properties
# find "${DOMAIN_DIR}/applications/dataverse/WEB-INF/classes" -type f -name '*.properties' -exec cp {} "${PROP_DIR}" \;

# Apply metatadata customization
echo '  - generate metadata properties'
for f in "$(data_dir metadatablocks)"/*.tsv "$(custom_dir metadatablocks)"/*.tsv
do
  PROP_FILE=$(basename -s '.tsv' $f)
  PROP_FILE="${PROP_FILE#*-}"
  echo "    - ${PROP_FILE} block"
  PROP_FILE="${PROP_DIR}/${PROP_FILE}.properties"
  rm -f "$PROP_FILE"
  SECTION=''
  while IFS=$"\n" read -r line
  do
    read_tdf_line a b c d e rest <<<$line
    [ "${a::1}" = '#' ] && SECTION="${a:1}" && continue
    [ "$SECTION" = '' ] && continue
    case $SECTION in
      "metadataBlock")
        echo "metadatablock.name=$b" >> "$PROP_FILE"
        echo "metadatablock.displayName=$d" >> "$PROP_FILE"
        ;;
      "datasetField")
        echo "datasetfieldtype.$b.title=$c" >> "$PROP_FILE"
        echo "datasetfieldtype.$b.description=$d" >> "$PROP_FILE"
        echo "datasetfieldtype.$b.watermark=$e" >> "$PROP_FILE"
        ;;
      "controlledVocabulary")
        x="$( echo $c | iconv -f UTF8 -t ASCII//TRANSLIT )"
        x="${x,,}"
        x="${x// /_}"
        y="$( echo -n $c | while IFS='' read -n 1 u; do [ "$u" = " " ] && echo -n ' ' && continue; printf -v cp '%d' \'$u; [[ $cp -gt 127 ]] && printf '\\u%04X' "'$u" || echo -n "$u"; done )"
        echo "controlledvocabulary.$b.$x=$y" >> "$PROP_FILE"
        ;;
    esac
  done < $f
done

# Customize text
echo "  - customize text entries"
for f in $(custom_dir properties)/*.json
do
  title=$(jq -r '.title' $f)
  echo "    - $title"
  jq -r '.data[]|[.name, .value]|@tsv' $f | while IFS=$'\t' read -r name value
  do
    PROP_FILE="${PROP_DIR}/${name%#*}"
    name="${name#*#}"
    if [ "$(grep -E "^${name}=" "$PROP_FILE" 2&>1 > /dev/null; echo $?)" = "0" ]
    then
      sed -i -e "s&^${name}=.*&${name}=$(echo "$value" | sed -e 's/&/\\&/')&" "$PROP_FILE"
    else
      echo "${name}=${value}" >> "$PROP_FILE"
    fi
  done
done

# Configure domain to use language dir
if ! echo 'y' | ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} list-jvm-options | grep -E '^-Ddataverse.lang.directory=' 2>&1 > /dev/null
then
  echo "  - set JVM language directory"
  echo 'y' | ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} create-jvm-options '-Ddataverse.lang.directory=/languages'
fi

echo