FROM fedora:29
MAINTAINER Andrej Rode <mail@andrejro.de>

ENV security_updates_as_of 2019-05-14

RUN dnf install -y \
# General building
        ccache \
        cmake \
        make \
        gcc \
        gcc-c++ \
        python3-pip \
        shadow-utils \
        xz \
# Build infrastructure
        cmake \
        boost-devel \
        python3-devel \
        python-devel \
        swig \
        cppunit-devel \
# Documentation
        doxygen \
        doxygen-latex \
        graphviz \
        python2-sphinx \
# Math libraries
        fftw-devel \
        gsl-devel \
        numpy \
        scipy \
        python3-scipy \
        gmp-devel \
# IO libraries
        SDL-devel \
        alsa-lib-devel \
        portaudio-devel \
        libsndfile-devel \
# because fedora is too stupid to install dependencies
       jack-audio-connection-kit \
        cppzmq-devel \
        python-zmq \
        uhd-devel \
## Gnuradio deprecated gr-comedi
## http://gnuradio.org/redmine/issues/show/395
        comedilib-devel \
## Vocoder libraries
        codec2-devel \
        gsm-devel \
# ctrlport - thrift
        thrift \
        thrift-devel \
# GUI libraries
        wxPython-devel \
        PyQt4-devel \
        xdg-utils \
        PyQwt-devel\
        qwt-devel \
# XML Parsing / GRC
        python-lxml \
        python-cheetah \
        pygtk2-devel \
        desktop-file-utils \
# next
        python-mako \
        python3-mako \
        python3-zmq \
        log4cpp-devel \
        PyQt5-devel \
        python3-PyQt5 \
        python3-click \
        python3-click-plugins \
        python2-click \
        python2-click-plugins \
# GRC/next
        PyYAML \
        python3-PyYAML \
        python-lxml \
        python3-lxml \
        python-gobject \
        python3-gobject \
        pycairo \
        python3-cairo \
        pango \
        && \
        dnf clean all && \
        # Test runs produce a great quantity of dead grandchild processes.  In a
        # non-docker environment, these are automatically reaped by init (process 1),
        # so we need to simulate that here.  See https://github.com/Yelp/dumb-init
        curl -Lo /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.1.3/dumb-init_1.1.3_amd64 && \
        chmod +x /usr/local/bin/dumb-init

COPY buildbot.tac /buildbot/buildbot.tac

        # ubuntu pip version has issues so we should upgrade it: https://github.com/pypa/pip/pull/3287
RUN     pip3 install -U pip virtualenv
        # Install required python packages, and twisted
RUN     pip3 --no-cache-dir install \
            'buildbot-worker' \
            'twisted[tls]' && \
            useradd -u 2017 -ms /bin/bash buildbot && chown -R buildbot /buildbot && \
            echo "max_size = 20G" > /etc/ccache.conf

RUN    mkdir -p /src/volk && cd /src && curl -Lo volk.tar.gz https://github.com/gnuradio/volk/archive/v2.1.0.tar.gz && tar xzf volk.tar.gz -C volk --strip-components=1 && cmake -DCMAKE_BUILD_TYPE=Release -S ./volk/ -B build && cd build && cmake --build . && cmake --build . --target install && cd / && rm -rf /src/volk && rm -rf /src/build

RUN    mkdir -p /src/pybind11 && cd /src && curl -Lo pybind11.tar.gz https://github.com/pybind/pybind11/archive/v2.4.3.tar.gz && tar xzf pybind11.tar.gz -C pybind11 --strip-components=1 && mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release -DPYBIND11_TEST=OFF ../pybind11/ && make && make install && cd / && rm -rf /src/pybind11 && rm -rf /src/build

USER buildbot

WORKDIR /buildbot

CMD ["/usr/local/bin/dumb-init", "twistd", "-ny", "buildbot.tac"]
