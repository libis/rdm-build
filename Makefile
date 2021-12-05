RDM_STAGE ?= dev

include env.$(RDM_STAGE)
export

.SILENT:
SHELL = /bin/bash

define help-targets
	awk -F ':|## ' '/^[^\t]+\s*:[^#]*## / {printf "    \033[36m%-30s\033[0m %s\n", $$1, $$NF}' $(1)
endef

define HELPTEXT

usage: help <command>
		
endef

# Set USER_ID and GROUP_ID to current user's uid and gid
USER_ID ?= $(shell id -u)
GROUP_ID ?= $(shell id -g)

# task comments starting with double # will be part of the help list

help: ## Show list and info on common tasks
	@echo "$$HELPTEXT"
	$(call help-targets, $(MAKEFILE_LIST))

build: build-index build-mailcatcher build-proxy build-dataverse build-tools ## Build all custom docker images

push: push-index push-mailcatcher push-proxy push-dataverse push-tools ## Publish all custom docker images

# DEVELOPMENT TASKS
######################################################################################################################

download_dataverse: ## Download the Dataverse installation package
	rm -f dvinstall.zip
	echo "Downloading Dataverse installation package ..."
	wget --quiet -nc -c https://github.com/IQSS/dataverse/releases/download/v$(DATAVERSE_VERSION)/dvinstall.zip || true
	rm -fr dvinstall/
	echo "Unzipping package ..."
	unzip -q dvinstall.zip

CP=rsync --info=name1,name2,del -ptgo

copy_dataverse: download_dataverse ## Distribute the Dataverse installation files to the images
	echo "Copying installation files ..."
	echo "  ... war file"
	$(CP) dvinstall/dataverse.war                          images/dataverse/dataverse.war
	echo "  ... metadata blocks"
	$(CP) dvinstall/data/metadatablocks/citation.tsv       images/dataverse/dvinstall/data/metadatablocks/01-citation.tsv
	$(CP) dvinstall/data/metadatablocks/geospatial.tsv     images/dataverse/dvinstall/data/metadatablocks/02-geospatial.tsv
	$(CP) dvinstall/data/metadatablocks/social_science.tsv images/dataverse/dvinstall/data/metadatablocks/03-social_science.tsv
	$(CP) dvinstall/data/metadatablocks/astrophysics.tsv   images/dataverse/dvinstall/data/metadatablocks/04-astrophysics.tsv
	$(CP) dvinstall/data/metadatablocks/biomedical.tsv     images/dataverse/dvinstall/data/metadatablocks/05-biomedical.tsv
	$(CP) dvinstall/data/metadatablocks/journals.tsv       images/dataverse/dvinstall/data/metadatablocks/06-journals.tsv
	echo "  ... authentication providers"
	$(CP) dvinstall/data/authentication-providers/builtin.json images/dataverse/dvinstall/data/authentication-providers/01-builtin.json
	echo "  ... roles"
	$(CP) dvinstall/data/role-admin.json                   images/dataverse/dvinstall/data/roles/01-admin.json
	$(CP) dvinstall/data/role-filedownloader.json          images/dataverse/dvinstall/data/roles/02-filedownloader.json
	$(CP) dvinstall/data/role-fullContributor.json         images/dataverse/dvinstall/data/roles/03-fullContributor.json
	$(CP) dvinstall/data/role-dvContributor.json           images/dataverse/dvinstall/data/roles/04-dvContributor.json
	$(CP) dvinstall/data/role-dsContributor.json           images/dataverse/dvinstall/data/roles/05-dsContributor.json
	$(CP) dvinstall/data/role-editor.json                  images/dataverse/dvinstall/data/roles/06-editor.json
	$(CP) dvinstall/data/role-curator.json                 images/dataverse/dvinstall/data/roles/07-curator.json
	$(CP) dvinstall/data/role-member.json                  images/dataverse/dvinstall/data/roles/08-member.json
	echo "  ... root collection"
	$(CP) dvinstall/data/dv-root.json                      images/dataverse/dvinstall/data/dv-root.json
	echo "  ... system admin"
	$(CP) dvinstall/data/user-admin.json                   images/dataverse/dvinstall/data/user-admin.json
	echo "  ... jhove configuration"
	$(CP) dvinstall/jhove.conf                             images/dataverse/dvinstall/jhove.conf
	$(CP) dvinstall/jhoveConfig.xsd                        images/dataverse/dvinstall/jhoveConfig.xsd
	echo "  ... Solr configuration"
	$(CP) dvinstall/schema.xml                             images/solr/conf/schema.xml
	$(CP) dvinstall/solrconfig.xml                         images/solr/conf/solrconfig.xml
	$(CP) dvinstall/update-fields.sh                       images/solr/scripts/update-fields.sh
	
build-dataverse: ## Create the docker image for the dataverse service
	echo "Building Dataverse image '$(DATAVERSE_IMAGE_TAG)'..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
			--build-arg PAYARA_VERSION=$(PAYARA_VERSION) --build-arg DATAVERSE_VERSION=$(DATAVERSE_VERSION) \
			-t $(DATAVERSE_IMAGE_TAG) ./images/dataverse

build-index: ## Create the docker image for the index service (Solr)
	echo "Building Index image '$(SOLR_IMAGE_TAG)'..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
			--build-arg SOLR_VERSION=$(SOLR_VERSION) \
			-t $(SOLR_IMAGE_TAG) ./images/solr

build-mailcatcher: ## Create the docker image for the mail catcher service
	echo "Building Mail catcher image '$(MAIL_CATCHER_IMAGE_TAG)'..."
	docker build -q -t $(MAIL_CATCHER_IMAGE_TAG) ./images/mailcatcher	

build-proxy: ## Create the docker image for the Shibboleth Service Provider
	echo "Building Proxy image '$(PROXY_IMAGE_TAG)'..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
		-t $(PROXY_IMAGE_TAG) ./images/proxy

download-tools:
	if ! [[ -d rdmPyTools ]]; then \
		echo "Cloning rdmPyTools ..."; git clone git@github.com:libis/rdmPyTools.git; \
	else \
		echo "Updating rdmPyTools ..."; cd rdmPyTools; git pull; cd -; \
	fi

update-tools: download-tools
	echo "Updating Gem bundle ..."
	cd images/tools; bundle update; cd -
	$(CP) --delete --dirs rdmPyTools/bin/*.py images/tools/rdmPyTools/

build-tools: update-tools ## Create the docker image for the Tools service
	echo "Building Tools image '$(TOOLS_IMAGE_TAG)'..."
	docker build -q --build-arg APP_USER_ID=$(USER_ID) --build-arg APP_GROUP_ID=$(GROUP_ID) \
		-t $(TOOLS_IMAGE_TAG) ./images/tools

push-dataverse: ## Publish the docker image for the dataverse service
	docker push $(DATAVERSE_IMAGE_TAG)

push-index: ## Publish the docker image for the index service (Solr)
	docker push $(SOLR_IMAGE_TAG)

push-mailcatcher: ## Publish the docker image for the mail catcher service
	docker push $(MAIL_CATCHER_IMAGE_TAG)

push-proxy: ## Publish the docker image for the Shibboleth Service Provider
	docker push $(PROXY_IMAGE_TAG)

push-tools: ## Publish the docker image for the Tools service
	docker push $(TOOLS_IMAGE_TAG)
