FROM centos:8

# s6-overlay version
ARG S6_OVERLAY_VERSION=2.2.0.3
ARG S6_OVERLAY_MD5=e49a47715f5f187928c98e6eaba41a39

# Set proper locale
ENV LC_ALL=C.UTF-8

# Install:
# - apache web server v 2.4
# - shibboleth
# - s6-overlay
# And:
# - remove default web server configuration files
RUN echo "Installing web server ..." \
 && rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial \
 && dnf install --skip-broken --rpmverbosity=critical --nodocs -q -y wget httpd mod_ssl \
 && echo "Installing Shibboleth ..." \
 && wget --no-verbose --quiet -O /etc/yum.repos.d/security:shibboleth.repo  \
    http://download.opensuse.org/repositories/security:/shibboleth/CentOS_8/security:shibboleth.repo \
 && dnf install --skip-broken --rpmverbosity=critical --nodocs -q -y --nogpgcheck shibboleth.x86_64 shibboleth-embedded-ds \
 && echo "Installing S6 Overlay ..." \
 && wget --no-verbose --quiet -O /tmp/s6-overlay.tgz \
    https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-amd64.tar.gz \
 && echo "${S6_OVERLAY_MD5} */tmp/s6-overlay.tgz" | md5sum -c - \
 && tar xzf /tmp/s6-overlay.tgz -C / --exclude="./bin" \
 && tar xzf /tmp/s6-overlay.tgz -C /usr ./bin \
 && rm -f /tmp/s6-overlay.tgz \
 && echo "Cleaning up ..." \
 && dnf clean all -q -y \
 && rm -rf /var/cache/yum

# Custom attributes-map.xml for Dataverse
COPY attribute-map.xml /etc/shibboleth/

# s6-overlay supervisor
ENTRYPOINT [ "/init" ]

# s6-overlay service scripts
COPY services.d/ /etc/services.d/
COPY fix-attrs.d/ /etc/fix-attrs.d/

# Change IDs for user and group shibd
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN find / -xdev -user shibd -exec chown ${USER_ID} {} \;  \
 && find / -xdev -group shibd -exec chgrp ${GROUP_ID} {} \;  \
 && groupmod --gid ${GROUP_ID} shibd  \
 && usermod --uid ${USER_ID} shibd