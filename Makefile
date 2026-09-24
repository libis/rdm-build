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

build:build-proxy build-dataverse build-previewers ## Build all custom docker images

push: push-proxy push-dataverse push-previewers ## Publish all custom docker images

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

DATAVERSE_GIT ?= https://github.com/IQSS/dataverse.git
# where to fetch the commits of patch.txt from; a local checkout, to test commits that are not pushed yet
PATCH_SOURCE ?= origin
PATCHED_DIR = images/dataverse/git

build-patched-dataverse: ## Create the dataverse image from v$(DATAVERSE_VERSION) with the commits of images/dataverse/patch.txt
	echo "Checking out Dataverse v$(DATAVERSE_VERSION) in $(PATCHED_DIR)..."
	if [ -d "$(PATCHED_DIR)" ]; then git -C $(PATCHED_DIR) fetch -q --tags origin; \
		else git clone -q --filter=blob:none $(DATAVERSE_GIT) $(PATCHED_DIR); fi
	git -C $(PATCHED_DIR) cherry-pick --quit 2>/dev/null || true # leftover of a failed run
	git -C $(PATCHED_DIR) checkout -q -f --detach v$(DATAVERSE_VERSION)
	git -C $(PATCHED_DIR) clean -q -fdx
	commits=$$(sed -e 's/#.*//' images/dataverse/patch.txt | xargs); \
		echo "Cherry-picking $$commits..."; \
		git -C $(PATCHED_DIR) fetch -q $(PATCH_SOURCE) $$commits && \
		git -C $(PATCHED_DIR) cherry-pick --no-commit $$commits && \
		echo "build.number=patched" > $(PATCHED_DIR)/src/main/java/BuildNumber.properties
	echo "Building Dataverse war file..."
	cd $(PATCHED_DIR) && mvn -q -Dmaven.test.skip=true clean package
	cp $(PATCHED_DIR)/target/dataverse-$(DATAVERSE_VERSION).war images/dataverse/
	echo "Building Dataverse image '$(DATAVERSE_IMAGE_TAG)_patched'..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
			--build-arg BASE_VERSION=$(BASE_VERSION) --build-arg DATAVERSE_WAR_URL=dataverse-$(DATAVERSE_VERSION).war \
			-t $(DATAVERSE_IMAGE_TAG)_patched ./images/dataverse

build-proxy: ## Create the docker image for the Shibboleth Service Provider
	echo "Building Proxy image '$(PROXY_IMAGE_TAG)'..."
	docker build -q --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) \
		-t $(PROXY_IMAGE_TAG) ./images/proxy

build-previewers: ## Create the docker image for previewers
	if [ -d "images/previewers/git" ]; then pushd images/previewers/git; git checkout ${PREVIEWERS_BRANCH}; git pull; popd; \
		else git clone ${PREVIEWERS_GIT} images/previewers/git; pushd images/previewers/git; git checkout ${PREVIEWERS_BRANCH}; popd; fi
	if [ -d "images/previewers/dvwebloader" ]; then pushd images/previewers/dvwebloader; git pull; popd; \
		else git clone https://github.com/libis/dvwebloader.git images/previewers/dvwebloader; fi
	if [ -d "images/previewers/cdi-viewer" ]; then pushd images/previewers/cdi-viewer; git pull; popd; \
		else git clone https://github.com/libis/cdi-viewer.git images/previewers/cdi-viewer; fi
	echo "Building CDI Viewer bundle..."
	cd images/previewers/cdi-viewer && npm install --ignore-scripts && npm run build
	echo "Building previewers image '$(PREVIEWERS_IMAGE_TAG)'..."
	docker build --no-cache -t $(PREVIEWERS_IMAGE_TAG) ./images/previewers

push-dataverse: ## Publish the docker image for the dataverse service
	docker push $(DATAVERSE_IMAGE_TAG)

push-patched-dataverse: ## Publish the patched docker image for the dataverse service
	docker push $(DATAVERSE_IMAGE_TAG)_patched

push-proxy: ## Publish the docker image for the Shibboleth Service Provider
	docker push $(PROXY_IMAGE_TAG)

push-previewers: ## Publish the docker image for the previewers
	docker push $(PREVIEWERS_IMAGE_TAG)