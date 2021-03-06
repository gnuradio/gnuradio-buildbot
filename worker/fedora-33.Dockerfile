FROM fedora:33
MAINTAINER Andrej Rode <mail@andrejro.de>

ENV security_updates_as_of 2020-12-19

# F30's container seems slightly broken due to a maintenance oversight when originally
# setting up the repos. We need to disable zchunk before using dnf. WTH.
RUN echo "zchunk=false" >> /etc/dnf/dnf.conf && \
    dnf install -y \
# General building
        ccache \
        ccache-swig \
        cmake \
        make \
        gcc \
        gcc-c++ \
        shadow-utils \
        xz \
# Build infrastructure
        cmake \
        boost-devel \
        python3-devel \
        swig \
        pybind11-devel \
        cppunit-devel \
# Documentation
        doxygen \
        # disabling doxygen-latex for build speed reasons.
#        doxygen-latex \ 
        graphviz \
        python3-sphinx \
# Math libraries
        fftw-devel \
        gsl-devel \
        python3-numpy \
        python3-scipy \
        gmp-devel \
# IO libraries
        cppzmq-devel \
        python3-zmq \
        SDL-devel \
        alsa-lib-devel \
        portaudio-devel \
        jack-audio-connection-kit \
        uhd-devel \
        log4cpp-devel \
## Vocoder libraries
        codec2-devel \
        gsm-devel \
# ctrlport - thrift
        thrift \
        thrift-devel \
        python3-thrift \
# GUI libraries
        xdg-utils \
        qwt-qt5-devel \
        python3-PyQt5 \
        python3-qt5-devel \
# XML Parsing / GRC
        desktop-file-utils \
        python3-mako \
        python3-click \
        python3-click-plugins \
# GRC/next
        python3-pyyaml \
        python3-lxml \
        python3-gobject \
        gtk3 \
        python3-cairo \
        pango \
        && \
    dnf clean all && \
    echo "max_size = 20G" > /etc/ccache.conf

COPY buildbot.tac /buildbot/buildbot.tac

        # Install required python packages, and twisted
RUN dnf install -y \
        git \
#buildbot infra
        python3-pip \
        python3-virtualenv \
        python3-twisted \
	python3-future \
        # Test runs produce a great quantity of dead grandchild processes.  In a
        # non-docker environment, these are automatically reaped by init (process 1),
        # so we need to simulate that here.  See https://github.com/Yelp/dumb-init
        dumb-init && \
    dnf clean all && \
    pip3 --no-cache-dir install 'buildbot-worker' && \
    useradd -u 2017 -ms /bin/bash buildbot && \
  chown -R buildbot /buildbot

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

CMD ["/usr/bin/dumb-init", "twistd", "-ny", "buildbot.tac"]
