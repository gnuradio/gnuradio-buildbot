FROM gnuradio/buildbot-worker:debian-10
MAINTAINER Andrej Rode <mail@andrejro.de>

ENV security_updates_as_of 2020-04-07
ENV VOLK_VERSION v2.2.1

USER root
WORKDIR /src

RUN git clone --depth=1 -b ${VOLK_VERSION} https://github.com/gnuradio/volk.git ./
RUN mkdir /build && cd build && cmake ../ && make -j2 && make install

USER buildbot
WORKDIR /buildbot
