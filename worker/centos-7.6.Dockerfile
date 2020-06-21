FROM centos:7.6.1810
MAINTAINER Andrej Rode <mail@andrejro.de>

ENV security_updates_as_of 2018-12-04

# enable EPEL for all the newer crazy stuff
# like CMake 3
RUN yum install epel-release -y -q && \
# get the new packages from EPEL
        yum --enablerepo=epel check-update -y; \
        yum install -y \
# General building
        ccache \
        cmake3 \
        make \
        swig3 \
        gcc \
        gcc-c++ \
        python36-pip \
        shadow-utils \
        openssl-devel \
# Build infrastructure
        boost-devel \
        python36-devel \
        python-devel \
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
        python36-scipy \
        gmp-devel \
# IO libraries
        SDL-devel \
        alsa-lib-devel \
        portaudio-devel \
        cppzmq-devel \
        python-zmq \
        python36-zmq \
        uhd-devel \
# ctrlport - thrift
        thrift \
        thrift-devel \
# GUI libraries
        xdg-utils \
        python-lxml \
        python36-lxml \
        python-cheetah \
        pygtk2-devel \
        desktop-file-utils \
        python-mako \
        log4cpp-devel \
        qt5-qtbase-devel \
        python36-qt5 \
        python36-pyqt5-sip \
        qwt-devel \
# GRC/next
        PyYAML \
        python36-PyYAML \
        gtk3 \
        python-gobject \
        python36-gobject \
        pycairo \
        python36-cairo \
        pango \
        && \
        yum clean all && \
        rm /usr/bin/python3 && \
        ln -s /usr/bin/python3.6 /usr/bin/python3
# download all the source RPMs we'll build later
RUN     cd && \
# symlink cmake3 and ctest3 to cmake / ctest
        cd /usr/bin && \
        ln -s ctest3 ctest && \
        ln -s cmake3 cmake && \
        yum clean all && \
        pip3 --no-cache-dir install 'mako' && \
        # Test runs produce a great quantity of dead grandchild processes.  In a
        # non-docker environment, these are automatically reaped by init (process 1),
        # so we need to simulate that here.  See https://github.com/Yelp/dumb-init
        curl -Lo /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.1.3/dumb-init_1.1.3_amd64 && \
        chmod +x /usr/local/bin/dumb-init

COPY buildbot.tac /buildbot/buildbot.tac

        # Install required python packages, and twisted
RUN     pip3 --no-cache-dir install \
            'buildbot-worker' \
            'twisted[tls]' && \
            useradd -u 2017 -ms /bin/bash buildbot && chown -R buildbot /buildbot && \
            echo "max_size = 20G" > /etc/ccache.conf

RUN    mkdir -p /src/volk && \
  cd /src && \
  curl -Lo volk.tar.gz https://github.com/gnuradio/volk/archive/v2.1.0.tar.gz && \
  tar xzf volk.tar.gz -C volk --strip-components=1 && \
  cmake -DCMAKE_BUILD_TYPE=Release -S ./volk/ -B build && \
  cd build && \
  cmake --build . && \
  cmake --build . --target install && \
  cd / && \
  rm -rf /src/volk && \
  rm -rf /src/build

RUN    mkdir -p /src/pybind11 && \
  cd /src && \
  curl -Lo pybind11.tar.gz https://github.com/pybind/pybind11/archive/v2.4.3.tar.gz && \
  tar xzf pybind11.tar.gz -C pybind11 --strip-components=1 && \
  mkdir build && \
  cd build && \
  cmake -DCMAKE_BUILD_TYPE=Release -DPYBIND11_TEST=OFF ../pybind11/ && \
  make && \
  make install && \
  cd / && \
  rm -rf /src/pybind11 && \
  rm -rf /src/build

USER buildbot

WORKDIR /buildbot

CMD ["/usr/local/bin/dumb-init", "twistd", "-ny", "buildbot.tac"]
