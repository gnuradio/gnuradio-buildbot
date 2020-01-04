FROM ubuntu:18.04
MAINTAINER Andrej Rode <mail@andrejro.de>

ENV security_updates_as_of 2019-05-14

# Prepare distribution
RUN apt-get update -q \
    && apt-get -y upgrade

# CPP deps
RUN DEBIAN_FRONTEND=noninteractive \
       apt-get install -qy \
         libasound2 \
         libboost-date-time1.65.1 \
         libboost-filesystem1.65.1 \
         libboost-program-options1.65.1 \
         libboost-thread1.65.1 \
         libcomedi0 \
         libfftw3-bin \
         libgmp10 \
         libgsl23 \
         libgtk-3-0 \
         libjack-jackd2-0 \
         liblog4cpp5v5 \
         libpangocairo-1.0-0 \
         libportaudio2 \
         libqwt6abi1 \
         libsdl-image1.2 \
         libuhd003.010.003 \
         libusb-1.0-0 \
         libzmq5 \
         libpango-1.0-0 \
         gir1.2-gtk-3.0 \
         gir1.2-pango-1.0 \
         pkg-config \
         --no-install-recommends \
    && apt-get clean

# Py deps
RUN DEBIAN_FRONTEND=noninteractive \
       apt-get install -qy \
         python-cheetah \
         python-click \
         python-click-plugins \
         python-dev \
         python-gi \
         python-gi-cairo \
         python-gtk2 \
         python-lxml \
         python-mako \
         python-numpy \
         python-opengl \
         python-qt4 \
         python-pyqt5 \
         python-wxgtk3.0 \
         python-yaml \
         python-zmq \
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
         python-wxgtk3.0 \
         python3-yaml \
         python3-zmq \
         python-six \
         python3-six \
         --no-install-recommends \
    && apt-get clean

# Build deps
RUN mv /sbin/sysctl /sbin/sysctl.orig \
    && ln -sf /bin/true /sbin/sysctl \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
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
       libcomedi-dev \
       libcppunit-dev \
       libfftw3-dev \
       libgmp-dev \
       libgsl0-dev \
       liblog4cpp5-dev \
       libqt4-dev \
       libqwt-dev \
       libqwt5-qt4 \
       libqwt-qt5-dev \
       qtbase5-dev \
       libsdl1.2-dev \
       libuhd-dev \
       libusb-1.0-0-dev \
       libzmq3-dev \
       portaudio19-dev \
       pyqt4-dev-tools \
       pyqt5-dev-tools \
       python-cheetah \
       python-sphinx \
       doxygen \
       doxygen-latex \
       swig \
    && rm -f /sbin/sysctl \
    && ln -s /usr/bin/ccache /usr/lib/ccache/cc \
    && ln -s /usr/bin/ccache /usr/lib/ccache/c++ \
    && mv /sbin/sysctl.orig /sbin/sysctl

# Testing deps
RUN DEBIAN_FRONTEND=noninteractive \
       apt-get install -qy \
       xvfb \
       lcov \
       python3-scipy \
       python-scipy \
       --no-install-recommends \
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

# Work around broken scan.coverity.com certificates
RUN curl -s -L https://entrust.com/root-certificates/entrust_l1k.cer -o /usr/local/share/ca-certificates/entrust_l1k.crt && update-ca-certificates

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

USER buildbot

WORKDIR /buildbot

CMD ["/usr/local/bin/dumb-init", "twistd", "-ny", "buildbot.tac"]
