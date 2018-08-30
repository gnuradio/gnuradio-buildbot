FROM fedora:28
MAINTAINER Andrej Rode <mail@andrejro.de>

ENV security_updates_as_of 2018-08-27

RUN dnf install -y \
# General building
        ccache \
        cmake \
        make \
        gcc \
        gcc-c++ \
        python3-pip \
        shadow-utils \
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
        cppzmq-devel \
        python-zmq \
        uhd-devel \
## Gnuradio deprecated gr-comedi
## http://gnuradio.org/redmine/issues/show/395
        comedilib-devel \
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

USER buildbot

WORKDIR /buildbot

CMD ["/usr/local/bin/dumb-init", "twistd", "-ny", "buildbot.tac"]
