FROM debian:bullseye
MAINTAINER Andrej Rode <mail@andrejro.de>

ENV security_updates_as_of 2020-12-19

RUN apt-get update -q \
  && apt-get -y upgrade

  # CPP deps
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get install -qy \
  libasound2 \
  libfftw3-bin \
  libgmp10 \
  libgsl25 \
  libgtk-3-0 \
  libjack-jackd2-0 \
  liblog4cpp5v5 \
  libpangocairo-1.0-0 \
  libportaudio2 \
  libqwt-qt5-6 \
  libsdl-image1.2 \
  libsndfile1-dev \
  libuhd3.15.0 \
  libzmq5 \
  libpango-1.0-0 \
  gir1.2-gtk-3.0 \
  gir1.2-pango-1.0 \
  pkg-config \
  --no-install-recommends \
  && apt-get clean

# Py3 deps
RUN DEBIAN_FRONTEND=noninteractive \
       apt-get install -qy \
         python3-click \
         python3-click-plugins \
         python3-mako \
         python3-dev \
         python3-gi \
         python3-gi-cairo \
         python3-lxml \
         python3-numpy \
         python3-opengl \
         python3-pyqt5 \
         python3-yaml \
         python3-zmq \
         python3-six \
         --no-install-recommends \
    && apt-get clean

# Build deps
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
       --no-install-recommends \
       build-essential \
       ccache \
       cmake \
       libboost-date-time-dev \
       libboost-dev \
       libboost-filesystem-dev \
       libboost-program-options-dev \
       libboost-regex-dev \
       libboost-system-dev \
       libboost-test-dev \
       libboost-thread-dev \
       libcppunit-dev \
       libfftw3-dev \
       libgmp-dev \
       libgsl-dev \
       liblog4cpp5-dev \
       libqwt-qt5-dev \
       qtbase5-dev \
       libsdl1.2-dev \
       libuhd-dev \
       libusb-1.0-0-dev \
       libzmq3-dev \
       libgsm1-dev \
       libcodec2-dev \
       portaudio19-dev \
       pyqt5-dev-tools \
       python3-cheetah \
       python3-sphinx \
       doxygen \
       doxygen-latex \
       swig \
       pybind11-dev \
    && ln -s /usr/bin/ccache /usr/lib/ccache/cc \
    && ln -s /usr/bin/ccache /usr/lib/ccache/c++

# Testing deps
RUN DEBIAN_FRONTEND=noninteractive \
       apt-get install -qy \
       --no-install-recommends \
       xvfb \
       lcov \
       python3-scipy \
    && apt-get clean


# Buildbot worker
# Copy worker configuration

COPY buildbot.tac /buildbot/buildbot.tac

# Install buildbot dependencies
RUN apt-get -y install -q \
                git \
                subversion \
                libffi-dev \
                libssl-dev \
                python3-pip \
                curl

# Test runs produce a great quantity of dead grandchild processes.  In a
# non-docker environment, these are automatically reaped by init (process 1),
# so we need to simulate that here.  See https://github.com/Yelp/dumb-init
RUN         curl -Lo /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.1.3/dumb-init_1.1.3_amd64 && \
            chmod +x /usr/local/bin/dumb-init && \
# ubuntu pip version has issues so we should upgrade it: https://github.com/pypa/pip/pull/3287
            pip3 install -U pip virtualenv
# Install required python packages, and twisted
RUN         pip3 --no-cache-dir install \
                'twisted[tls]' \
                'buildbot_worker' \
                'xvfbwrapper' && \
    useradd -u 2017 -ms /bin/bash buildbot && chown -R buildbot /buildbot && \
    echo "max_size = 20G" > /etc/ccache.conf

RUN rm -rf /var/lib/apt/*

RUN mkdir -p /src/volk && \
 cd /src && \
 curl -Lo volk.tar.gz https://github.com/gnuradio/volk/releases/download/v2.4.1/volk-2.4.1.tar.gz && \
 tar xzf volk.tar.gz -C volk --strip-components=1 && \
 cmake -DCMAKE_BUILD_TYPE=Release -S ./volk/ -B build && \
 cd build && \
 cmake --build . && \
 cmake --build . --target install && \
 cd / && \
 rm -rf /src/volk && \
 rm -rf /src/build

USER buildbot
WORKDIR /buildbot

CMD ["/usr/local/bin/dumb-init", "twistd", "-ny", "buildbot.tac"]
