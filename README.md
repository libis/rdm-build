# rdm-build
*build scripts for the RDM docker images*

This repository contains the data and scripts that are needed to build the images used in our RDM repository installation.

We build 5 Docker images with this repository:

- dataverse : the main image that will be able to run the Dataverse application
- solr : a customized image that runs the covoc Solr index server
- dvsolr : a customized image that runs the Dataverse Solr index server
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

There are also targets for building and publishing a single image. Use the `help` target to list the other options.

## Dataverse image

The Dataverse image is almost the same as the stock Dataverse image, with only ruby additionally installed on top of the base image. For the details on the stock Dataverse image, see https://guides.dataverse.org/en/latest/container/index.html

## Solr image

The solr image is almost the same as the stock Sorl image, but has some small changes:

- The image will run as a given User ID and Group ID to facilitate backup and restore of the configuration and data

## DVSolr image

The dvsolr image is the same as the stock Sorl image.

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

A development test version of Dataverse can by run with docker compose as described at https://guides.dataverse.org/en/latest/container/index.html
