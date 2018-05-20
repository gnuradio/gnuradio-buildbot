# andrej/buildbot-master

# please follow docker best practices
# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/
#
# Provides a base alpine 3.4 image with latest buildbot master installed
# Alpine base build is ~130MB vs ~500MB for the ubuntu build

# Note that the UI and worker packages are the latest version published on pypi
# This is to avoid pulling node inside this container

FROM        alpine:3.7
MAINTAINER  Andrej Rode <mail@andrejro.de>

# Last build date - this can be updated whenever there are security updates so
# that everything is rebuilt
ENV         security_updates_as_of 2018-05-20


# We install as much as possible python packages from the distro in order to avoid
# having to pull gcc for building native extensions
# Some packages are at the moment (10/2016) only available on @testing
RUN \
    echo @testing http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories && \
    echo @edge http://nl.alpinelinux.org/alpine/edge/community >> /etc/apk/repositories && \
    apk add --no-cache \
        git \
        python3 \
        py3-psycopg2 \
        py3-cffi \
        py3-requests \
        py3-openssl@edge \
        py3-cryptography@edge \
        py3-service_identity@edge \
        py3-sqlalchemy@edge \
        gosu@testing \
        dumb-init@edge\
        py3-jinja2 \
        docker-py@edge \
        gcc \
        python3-dev \
        musl-dev \
        tar \
        curl
# install pip dependencies
RUN pip3 install docker-pycreds backports.ssl_match_hostname && \
    pip3 install --upgrade pip setuptools && \
    pip3 install --upgrade "twisted" "txrequests" && \
    rm -r /root/.cache

RUN pip3 install "buildbot[bundle,tls]"

WORKDIR /var/lib/buildbot
CMD ["dumb-init", "/var/lib/buildbot/start_buildbot.sh"]
