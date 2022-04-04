# rdm-build
*build scripts for the RDM docker images*

This repository contains the data and scripts that are needed to build the images used in our RDM repository installation.

We build 4 Docker images with this repository:

- dataverse : the main image that will be able to run the Dataverse application
- solr : a customized image that runs the Solr index server
- proxy : an image that provides a reverse proxy in front of all the containers. It will also run the Shibboleth SP server that protects the access to the applications.
- mailcatcher : an image that behaves as a mail server, but will not forward the emails to the user's mailboxes. Instead all emails are displayed in a web page.

There are two version of the images that can be built. De default image version is a local build and is used when deployment will happen to the local machine, typically in development environments.

The other image version is one that will be deployed on a test or production server and is built to be published to a docker repository.

You select which version of the image you will be building by setting the STAGE environment variable. The value `dev` - which is de default - will build local images, while the value `prod` will build repository images.

```
$ export STAGE=prod
```

The actions are enabled with make. The Makefile contains a limited set of targets:

- `build` : build all images
- `push` : publish the images to the repository
- `download_dataverse` : download the Dataverse installation package and prepare the files to be included in the images
- `copy_dataverse` : copy the files from the downloaded installation package into the image directory

There are also targets for building and publishing a single image. Use the `help` target to list the other options.

## Dataverse image

The dataverse image is based on a community version of the Payara server docker image. Payara is a Java EE / Jakarta application server.

It will make sure that the application is running as a given User ID and Group ID because a lot of data will be stored on host mounted volumes and needs to be accessible from the host user for maintenance tasks like backup and reporting.

The downloaded Dataverse installation files are be copied into the image to enable initialization of the Dataverse installation when the image is deployed. When building the image for the first time or when updating the Dataverse version, make sure you run the `download_dataverse` and `copy_dataverse` make tasks before building the image.

### image structure

- `bin` folder contains bash scripts that are used when the container is started or can be executed on demand.
  - `init_0_deploy_dataverse.sh` script that runs when the container is started
  - `builtin-users-*.sh` scripts that enable/disable the APIs to create builtin users
  - `security-*.sh` scripts that secure admin API by token/localhost-only
  - `bootstrap-job.sh` main script for bootstrapping the application
  - `config` library of functions for API calls
- `dvinstall` folder with setup scripts and data
  - `config-job.sh` script that sets database settings via environment variables
  - `jhove*` files that configure JHove in the application
  - `data` folder with data files for objects to create
  - `settings-update.sh` script that re-applies the settings data
  - `setup-once.sh` script dat scans the data files and performs the API actions to create the objects
  - `setup-tools` library of functions for data file actions

The Docker container will execute the `init_*.sh` scripts in alphabetical order when  booting the image. Our script will deploy the dataverse war file and prepare scripts for Payara's asadmin command to be executed when the application server starts. The script will skip its tasks when the application is already deployed.

The `bootstrap-job.sh` script needs to be called manually and should only be called when the application has started completely. It will delegate most of its work to the `setup-once.sh` and `config-job.sh` scripts. The first script will scan the `data` folder for files with data (mostly JSON) and execute API calls to load the data. The second script scans the environment for certain variables and configures the application from these.

The `data` folder contains the settings for a default and out-of-the-box installation of Dataverse. But the script will also look in a custom installation directory for data files that override or append the `data` files. Any file and subfolder in the custom `overwrite` folder will override the standard `data` files and folders. The subfolders in the custom `data` folder will be scanned in addition to the corresponding standard `data` subfolder or custom `overwrite` subfolder. In other words to process subfolder 'A':
- if subfolder 'A' exists in custom 'overwrite' folder, parse that folder
- otherwise, parse 'A' folder in the image standard `data` folder
- then, if subfolder 'A' exists in custom `data` folder, parse custom subfolder `A` too.

And similary for individual data files in the root of the standard `data` and custom folders.

### data folders

The data folders, either the standard data folder, the custom overwrite folder or the custom data folder, should contain the same structure. All data files should match the following regex: `^[[:digit:]]+(-\w+)+\.(json|tsv)$`. i.o.w. It should start with one or more digits, followed by one or more repetitions of a dash and a string, and finally a dot and a file extension. The file extension has to be 'json' in all cases except for the metadata blocks, where the file extension should be 'tsv'. *.json files should contain properly formatted JSON data and *.tsv files should be formatted as tab separated files.

- `dv-root.json` file with JSON data for the root Dataverse collection
- `user-admin.json` file with JSON data for the super administrator user
- `authentication-providers` folder with JSON data files for authentication providers
- `collections` folder for Dataverse collections

  each JSON data file in the folder will create a subcolletion

  the first string in the file name should contain the alias of the parent collection

  for each file in each of the subfolders, the first string in the file name should always contain the alias of the collection the action should be applied to
  
  - `facets` folder for facets for a Dataverse collection
  
    each data file should contain a JSON array that contains a list of metadata field names that should be presented as a facet

  - `group-assignments` folder for assigning users to a group in a Dataverse collection

    each data file should contain a JSON array with user names that should be added to the group

    the second string in the file name should contain the group name

  - `groups` folder with JSON data files for creating groups in a Dataverse collection

  - `metadatablocks` folder for selecting the metadata blocks of a Dataverse collection
    
    each data file should contain a JSON array with a list of the metadata blocks to enable for a given collection

  - `role-assignments` folder for assigning roles to groups in a Dataverse collection

    each data file should contain a JSON object with the assignee and role fields

  - `templates` folder for Dataset templates

    the data files in this folder will not be processed by the bootstrap process, because there is not yet an API to create Dataset templates

    instead the files contain the necessary data to create the templates by hand

- `metadatablocks` folder with metadata block definitions

  each file should be in the tab-separated-value format with the structure as specified in the Dataverse documentation

- `roles` folder for defining root-level roles

  each JSON data file defines a role and should contain the JSON object that will be supplied to the API

- `settings` folder with database settings

  each file should contain a JSON object with free to choose `title` field and `data` field containing an array of objects. Each data object should contain a `name` and `value` field containing the settings name and value. For a list of settings names see the Dataverse documentation regarding [Database Settings](https://guides.dataverse.org/en/latest/installation/config.html).

  You are free to organize the settings in different files, but be aware that the files will be processed in alphabetical order and repeated setting names will overwrite earlier defined values.

  To delete a setting set the value field to an empty string.

- `users` folder that creates builtin users

  each JSON data file defines the parameters for a single user

- `branding` folder that contains any (HTML) files needed for branding

### configuration

As explained above, the image allows customisation at run-time by supplying a custom install dir. That directory can be mounted anywhere in the file system as long as the `CUSTOM_INSTALL` environment variable points to that folder. This folder should be the parent folder of the `data` and `overwrite` subfolders.

Next to the subfolders the custom installation folder may also contain:

- `config-job.sh` script that configures the application; the script should be allowed to run multiple times
- `setup-once.sh` script that will be executed as part of the bootstrap task and contains additional configuration steps
- `preboot` file containing any additional asadmin commands that should be executed before the application server boots
- `postboot` file containing any additional asadmin commands that should be executed right after the application server boots
- any other custom script you may want to execute in the container

Other environment variables that configure the Dataverse installation are:

- `POSTGRES_SERVER` : the hostname of the database server
- `POSTGRES_PORT` : the port where the database server is listening on
- `POSTGRES_USER` : the user name part of the database credentials
- `POSTGRES_DATABASE` : the name of the database to connect to
- `SOLR_SERVICE_HOST` : the hostname of the index server
- `SOLR_SERVICE_PORT_HTTP` : the port where the index server is listening on
- `MAIL_SERVICE_HOST` : the hostname of the mail server
- `MAIL_FROMADDRESS` : the name of the user that mails are to be sent from
- `DATAVERSE_SERVICE_HOST` : the hostname to use to connect to - probably always to be set as 'localhost'
- `DATAVERSE_SERVICE_PORT_HTTP` : the port to use to connect to - probably always to be set as '8080'
- `dataverse_fqdn` : the fully qualified domain name (FQDN) for public access
- `dataverse_siteUrl` : the complete URL (including http/https prefix) for public access
- `doi_username` : the user name of the Datacite account
- `doi_baseurlstring` : the first portion of the Datacite URL
- `db_SystemEmail` : email address of the sender for system emails

Next to that the image expexts the following secrets to be set:

- `/run/secrets/db/password` : the password part of the database credentials
- `/run/secrets/admin/password` : the password for the super admin user
- `/run/secrets/user/password` : the default password for other users created by the bootstrap routine
- `/run/secrets/api/key` : API token to use
- `/run/secrets/api/userskey` : key for creating builtin users
- `/run/secrets/doi/password` : password for the Datacite account
- `/run/secrets/rserve/password` : password for the RServer account (not yet used)

## Solr image

The solr image is almost the same as the stock Sorl image, but has some small changes:

- The image will run as a given User ID and Group ID to facilitate backup and restore of the configuration and data
- Customised `solrconfig.xml` file by Dataverse
- Customised `schema.xml` file containing the Dataverse metadata schema
- `updateSchemaMDB.sh` script that synchronises the `schema.xml` with the Dataverse metadata blocks.

The update script requires the Dataverse API key and expects that to be available in either:
  - the `-u` optional command-line option
  - file with path in the `UNBLOCK_KEY` environment variable
  - the `UNBLOCK_KEY` environment variable

## Proxy image

This image will be the front-end of the application installation. It contains both an Apache web server and the Shibboleth daemon.

The configuration of the Apache server is to be defined at runtime by mounting configuration files in the /etc/httpd/conf.d folder, but it is expected that it will perform as a reverse proxy for the Dataverse container and can delegate certain paths to the Shibboleth plugin or other containers.

The image is built around the S6 Overlay tool that will monitor both the Apache server process and the Shibboleth daemon and restarts them in case they would stop running. The S6 Overlay functions as a init daemon, but is optmised for useage in a Docker container.

Configuration should be done by mounting Apache and Shibboleth configuration files and certificates in their appropriate locations.

## Mailcatcher image

Running only the Ruby-based mailcatcher tool, this image is very simple. Configuration options are limited to:

- `HTTP_PORT` environment variable : port where the web interface will listen on
- `SMTP_PORT` environment variable : port where the mail server will listen on

# Local test deployment

A local deployment configuration is included for testing purposes. You can find the test deployment in the `test` folder. All that is needed is a local docker installation and the `docker-compose` tool.

The installation is driven by the included `Makefile`. List the targets available with `make help`:

- `up`: start the stack
- `down`: shut down the stack
- `restart`: stop and start the stack
- `redeploy`: stops the stack, removes the docker volume where the application is deployed and starts the stack again
- `status`: shows the status of the stack services
- `tools`: run the tools image menu
- `reset`: stops and removes the stack and all the data; then starts the stack and initializes the application
