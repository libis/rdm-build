ARG MSMTP_VERSION=1.8.15

FROM alpine:latest AS download
RUN apk --update --no-cache add curl tar unzip xz gzip

ARG MSMTP_VERSION
WORKDIR /dist/msmtp
RUN curl -sSL "https://marlam.de/msmtp/releases/msmtp-$MSMTP_VERSION.tar.xz" | tar xJv --strip 1

FROM alpine:latest AS builder
RUN apk --update --no-cache add \
    autoconf \
    automake \
    binutils \
    build-base \
    gettext-dev \
    gnutls-dev \
    libidn2-dev \
    libgsasl-dev \
    libsecret-dev \
    openssl-dev \
  && rm -rf /tmp/*

COPY --from=download /dist/msmtp /tmp/msmtp
WORKDIR /tmp/msmtp
RUN ./configure \
    --prefix=/usr \
    --sysconfdir=/etc \
    --mandir=/usr/share/man \
    --localstatedir=/var \
  && make -j$(nproc) \
  && make install \
  && msmtp --version

FROM alpine:latest

# msmtp
COPY --from=builder /usr/bin/msmtp* /usr/bin/

RUN apk --update --no-cache add \
    bash \
    ca-certificates \
    gettext \
    gnutls \
    libidn2 \
    libgsasl \
    libsecret \
    mailx \
    openssl \
    shadow \
    tzdata \
  && ln -sf /usr/bin/msmtp /usr/sbin/sendmail \
  && ln -snf /usr/share/zoneinfo/Europe/Brussels /etc/localtime \
  && echo Europe/Brussels > /etc/timezone \
  && rm -rf /tmp/* /var/cache/apk/*

# s6-overlay
ADD https://github.com/just-containers/s6-overlay/releases/latest/download/s6-overlay-amd64.tar.gz /tmp/s6overlay.tar.gz
RUN tar xzf /tmp/s6overlay.tar.gz -C / \
 && rm /tmp/s6overlay.tar.gz \
 && for f in cont-init.d cont-finish.d fix-attrs.d services.d; do mkdir -p /etc/$f; done

COPY run /etc/services.d/msmtp/
COPY msmtprc /etc/
RUN chmod 755 /etc/services.d/msmtp/run

ENTRYPOINT [ "/init" ]
