include .env
export

.SILENT:
SHELL = /bin/bash

.PHONY: up

define help-targets
	awk -F ':|## ' '/^[^\t]+\s*:[^#]*## / {printf "    \033[36m%-30s\033[0m %s\n", $$1, $$NF}' $(1)
endef

define help-admins
	awk -F ':|### ' '/^[^\t]+\s*:[^#]*### / {printf "  * \033[36m%-30s\033[0m %s\n", $$1, $$NF}' $(1)
endef

define HELPTEXT

usage: help <command>
		
endef

define ADMINTEXT

Note: % stands for a service name, one of: dataverse db dbadmin proxy index

Note: Administrative tasks are indicated with an '*' in front of them. These tasks are intended 
      for trouble shooting. Do not run them unless you undestand the task action and its impact.
endef

# Set USER_ID and GROUP_ID to current user's uid and gid
USER_ID ?= $(shell id -u)
GROUP_ID ?= $(shell id -g)

# task comments starting with double # will be part of the help list
# task comments starting with triple # will be part of the help_admin list

help: ## Show list and info on common tasks
	@echo "$$HELPTEXT"
	$(call help-targets, $(MAKEFILE_LIST))
	$(call help-admins, $(MAKEFILE_LIST))
	@echo "$$ADMINTEXT"

.PHONY: up
up: ## Start or update all services
	docker-compose up -d proxy db index dataverse mail dbadmin apidoc

.PHONY: down
down: ## Stop and destroy all services
	docker-compose down
	@echo -n "Waiting for shutdown "
	@while [ $$(docker network ls --format {{.Name}} | grep 'test_.*_net' | wc -l) != '0' ]; do echo -n '.'; sleep 1; done && echo ' OK.'

.PHONY: restart
restart: down up wait_dv ## Stop and restart all services

.PHONY: status
status: ## List all running services
	docker-compose ps

.PHONY: tools
tools: ## Run tools container
	docker run --rm -it --network test_app_net -v $(PWD)/$(TOOLS_DATA):/opt/data -v $(PWD)/$(TOOLS_SCRIPTS):/opt/app/scripts -v $(PWD)/secrets:/run/secrets:ro \
		-e DATAVERSE_SERVICE_HOST=dataverse -e DATAVERSE_SERVICE_PORT_HTTP=8080 --hostname tools --name "tools-$$(date +'%Y%m%d-%H%M%S')" \
		$(TOOLS_IMAGE_TAG) bash -c ./menu.sh

.PHONY: shell
shell: ## Run shell in tools container
	docker run --rm -it --network test_app_net -v $(PWD)/$(TOOLS_DATA):/opt/data -v $(PWD)/$(TOOLS_SCRIPTS):/opt/app/scripts -v $(PWD)/secrets:/run/secrets:ro \
		-e DATAVERSE_SERVICE_HOST=dataverse -e DATAVERSE_SERVICE_PORT_HTTP=8080 --hostname tools --name "tools-$$(date +'%Y%m%d-%H%M%S')" \
		$(TOOLS_IMAGE_TAG) bash

# INITIALIZATION
######################################################################################################################
DIRS := $(DV_FILES) $(DV_DUMPS) $(DV_UPLOADS) $(DV_LANG_DIR) $(DB_DATA) $(INDEX_DATA) $(DOCROOT) \
				$(PROXY_LOGS)/httpd $(PROXY_LOGS)/shib $(DBADMIN_DATA) $(DBADMIN_LOGS) $(TOOLS_DATA) $(TOOLS_SCRIPTS)

.PHONY: reset ### Reset the installation - deletes all data, including database and index
reset: ### Stops all services and clears all the data. ALL DATA WILL BE PERMANENTLY LOST!!
	@echo "STAGE 1: Create clean installation"
	@echo "++++++++++++++++++++++++++++++++++"
	$(MAKE) down rmdirs mkdirs up wait_dv
	@echo "++++++++++++++++++++++++++++++++++"
	@echo "STAGE 2: Bootstrap and configuration"
	@echo "++++++++++++++++++++++++++++++++++++"
	$(MAKE) bootstrap solr_config stop-index stop-dataverse up wait_dv
	@echo "++++++++++++++++++++++++++++++++++"
	@echo "STAGE 3: Index configuration update"
	@echo "+++++++++++++++++++++++++++++++++++"
	$(MAKE) solr_update reindex stop-dataverse up wait_dv

.PHONY: customize
customize:
	docker-compose exec dataverse custominstall/customize-properties.sh

.PHONY: rmdirs
rmdirs:
	rm -fR $(DIRS)

.PHONY: mkdirs
mkdirs:
	mkdir -p $(DIRS)

.PHONY: bootstrap
bootstrap: ### First time configuration script for new dataverse installation
	docker-compose exec dataverse bootstrap-job.sh

.PHONY: solr_config
solr_config:
	cp ./config/solr/conf/solrconfig.xml ${INDEX_DATA}/data/collection1/conf/solrconfig.xml

.PHONY: solr_update
solr_update:
	docker-compose exec index updateSchema.sh -d http://dataverse:8080 -t /var/solr/data/collection1/conf -u /run/secrets/api/key || true

# ADMIN TASKS 
######################################################################################################################

wait_dv: ### Wait for Dataverse ready
	@echo -n "Waiting for Dataverse ready "
	@while [ "$$(curl -sk -m 1 -I $(DATAVERSE_URL_PREFIX)://localhost:7000/robots.txt | head -n 1|cut -d$$' ' -f2)" != "200" ]; do \
		[[ $$? -gt 0 ]] && echo -n 'x' || echo -n '.'; sleep 1; done && true
	@echo	' OK.'

log-%: ### Show log entries of service
	docker-compose logs --no-log-prefix $(*) 2>&1 | less -R

logf-%: ### Show real-time log entries of service
	docker-compose logs -f --no-log-prefix $(*) 2>&1

logf-proxy: 
	tail -f data/proxy/*/*.log

shell-%: ### start shell in running docker container
	docker-compose exec $(*) /bin/bash

stop-%: ### stop container
	docker-compose stop $(*)

.PHONY: reindex
reindex: ### Force reindexing of all Dataverse collections and datasets
	docker-compose exec dataverse /opt/payara/custominstall/reindex.sh
