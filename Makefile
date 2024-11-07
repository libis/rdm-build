STAGE ?= dev

include env.$(STAGE)
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

build:build-proxy build-dataverse ## Build all custom docker images

push: push-proxy push-dataverse ## Publish all custom docker images

# DEVELOPMENT TASKS
######################################################################################################################

build-dev-dataverse: ## Create the docker image for the develop dataverse
	echo "Building Dataverse war file from source..."
	cd ../dataverse; mvn -DskipTests=true clean package
	echo "Building development Dataverse image '$(DATAVERSE_IMAGE_TAG)'..."
	cd ..; docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
			--build-arg BASE_VERSION=$(BASE_VERSION) --build-arg DATAVERSE_WAR_URL=dataverse/target/dataverse-$(DATAVERSE_VERSION).war \
			-t $(DATAVERSE_IMAGE_TAG) --file rdm-build/images/dataverse/Dockerfile .

build-dataverse: ## Create the docker image for the dataverse service
	echo "Building Dataverse image '$(DATAVERSE_IMAGE_TAG)'..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
			--build-arg BASE_VERSION=$(BASE_VERSION) --build-arg DATAVERSE_WAR_URL=$(DATAVERSE_WAR_URL) \
			-t $(DATAVERSE_IMAGE_TAG) ./images/dataverse

build-proxy: ## Create the docker image for the Shibboleth Service Provider
	echo "Building Proxy image '$(PROXY_IMAGE_TAG)'..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
		-t $(PROXY_IMAGE_TAG) ./images/proxy

push-dataverse: ## Publish the docker image for the dataverse service
	docker push $(DATAVERSE_IMAGE_TAG)

push-proxy: ## Publish the docker image for the Shibboleth Service Provider
	docker push $(PROXY_IMAGE_TAG)
