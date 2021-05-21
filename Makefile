include .env
export

.SILENT:
SHELL = /bin/bash

.PHONY: up

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

build: build-index build-mail build-proxy build-dataverse ## Build all custom docker images

# DEVELOPMENT TASKS
######################################################################################################################

download_dataverse: ## Download the Dataverse installation package and distribute files
	rm -f dvinstall.zip
	echo "Downloading Dataverse installation package ..."
	wget --quiet -nc -c https://github.com/IQSS/dataverse/releases/download/v$(DATAVERSE_VERSION)/dvinstall.zip || true
	rm -fr dvinstall/
	echo "Unzipping package ..."
	unzip -q dvinstall.zip
	echo "Checking differences ..."
	for f in dataverse.war; \
	  do echo -n " - $$f: "; cmp -s images/dataverse/dvinstall/$$f dvinstall/$$f && echo "OK" || echo "!! DIFFERENT !!"; done || true
	for f in jhove.conf jhoveConfig.xsd; \
	  do echo -n " - $$f: "; diff -bq images/dataverse/dvinstall/$$f dvinstall/$$f &>/dev/null && echo "OK" || echo "!! DIFFERENT !!"; done || true
	for f in schema_dv_mdb_fields.xml schema.xml solrconfig.xml; \
	  do echo -n " - $$f: "; diff -bEq images/solr/conf/$$f dvinstall/$$f &>/dev/null && echo "OK" || echo "!! DIFFERENT !!"; done || true
	for f in updateSchemaMDB.sh; \
	  do echo -n " - $$f: "; diff -bq images/solr/scripts/$$f dvinstall/$$f &>/dev/null && echo "OK" || echo "!! DIFFERENT !!"; done || true
	
build-dataverse: ## Create the docker image for the dataverse service
	echo "Building Dataverse image ..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
			--build-arg PAYARA_VERSION=$(PAYARA_VERSION) --build-arg DATAVERSE_VERSION=$(DATAVERSE_VERSION) \
			-t $(DATAVERSE_IMAGE_TAG) ./images/dataverse

build-index: ## Create the docker image for the index service (Solr)
	echo "Building Index image ..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
			--build-arg SOLR_VERSION=$(SOLR_VERSION) \
			-t $(SOLR_IMAGE_TAG) ./images/solr

build-mail: ## Create the docker image for the mail catcher service
	echo "Building Mailcatcher image ..."
	docker build -q -t $(MAIL_IMAGE_TAG) ./images/mailcatcher	

build-proxy: ## Create the docker image for the Shibboleth Service Provider
	echo "Building Proxy image ..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
		-t $(PROXY_IMAGE_TAG) ./images/proxy
