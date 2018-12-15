FROM centos:7.6.1810
MAINTAINER Andrej Rode <mail@andrejro.de>

ENV security_updates_as_of 2018-12-04

# enable EPEL for all the newer crazy stuff
# like CMake 3
RUN yum install epel-release -y
# get the new packages from EPEL
RUN yum --disablerepo=* --enablerepo=epel check-update -y
RUN yum install -y \
# General building
        ccache \
        cmake3 \
        make \
        gcc \
        gcc-c++ \
        python34-pip \
        shadow-utils \
# for SWIG source build
        automake \
        autoconf \
        byacc \
# for QWT source build
        rpm-build \
        yum-utils \
# Build infrastructure
        boost-devel \
        python34-devel \
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
        python34-scipy \
        gmp-devel \
# IO libraries
        SDL-devel \
        alsa-lib-devel \
        portaudio-devel \
        cppzmq-devel \
        python-zmq \
        uhd-devel \
# ctrlport - thrift
        thrift \
        thrift-devel \
# GUI libraries
        xdg-utils \
# XML Parsing / GRC
        python-lxml \
        python-cheetah \
        pygtk2-devel \
        desktop-file-utils \
# next
        python-mako \
        log4cpp-devel \
        qt5-qtbase-devel \
# GRC/next
        PyYAML \
        python34-PyYAML \
        gtk3 \
        python-gobject \
        python34-gobject \
        pycairo \
        python34-cairo \
        pango \
        && \
        yum clean all && \
# download all the source RPMs we'll build later
        cd && \
        curl -L https://download.fedoraproject.org/pub/fedora/linux/releases/29/Everything/source/tree/Packages/s/sip-4.19.12-9.fc29.src.rpm > sip.src.rpm && \
        curl -L https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/Packages/p/python-qt5-5.11.3-1.fc30.src.rpm > python-qt5.src.rpm && \
        curl -L https://download.fedoraproject.org/pub/fedora/linux/releases/29/Everything/source/tree/Packages/q/qwt-6.1.3-9.fc29.src.rpm > qwt.src.rpm && \
        curl -L https://github.com/swig/swig/archive/rel-3.0.12.tar.gz > swig.tar.gz
RUN     cd ~ && \
# install and patch'em
        rpm -i sip.src.rpm && \
        rpm -i python-qt5.src.rpm && \
        rpm -i qwt.src.rpm && \
        cd rpmbuild/SPECS && \
        sed -i 's/BuildRequires: python%{python3_pkgversion}-enum34//' python-qt5.spec && \
        sed -i 's/%ldconfig_scriptlets.*$//' qwt.spec && \
# install the sip build dependencies
        yum-builddep -y sip.spec && \
# symlink cmake3 and ctest3 to cmake / ctest
        cd /usr/bin && \
        ln -s ctest3 ctest && \
        ln -s cmake3 cmake && \
# build and install sip backport first
        cd ~/rpmbuild/SPECS && \
        # build the binary package
        rpmbuild -bb sip.spec && \
        # install the freshly built binary and development rpms
        cd ../RPMS/x86_64/ && \
        rpm -i python2-pyqt5* python34-pyqt5* python2-sip-* python34-sip-* sip-4* && \
# build and install python-qt5 backport
        cd ~/rpmbuild/SPECS/ && \
        yum-builddep -y python-qt5.spec && \
        rpmbuild -bb python-qt5.spec && \
        cd ../RPMS/ && \
        rpm -i noarch/python-qt5-rpm-macros* x86_64/python2-qt5* x86_64/python34-qt5* && \
        # for some reason, we *must* clean the package database here
        yum clean all && \
# build and install qwt backport
        cd ~/rpmbuild/SPECS && \
        yum-builddep -y qwt.spec && \
        rpmbuild -bb qwt.spec && \
        cd ../RPMS/x86_64 && \
        rpm -i qwt-6*.rpm qwt-devel*.rpm qwt-qt5*.rpm && \
# finally, clear yum cache
        yum clean all && \
# our special friend SWIG...
        cd && \
        tar xzf swig.tar.gz && \
        cd swig-rel-3.0.12 && \
        ./autogen.sh && \
        ./configure --without-pcre --prefix=/usr && \
        make -j8 && \
        make install && \
# lastly, clean up:
        cd && \
        rm -rf rpmbuild swig-rel-3.0.12 *.src.rpm

# We'll need mako, since EPEL doesn't have python34-mako, we'll install it via pip3:
# same for pyzmq and lxml
RUN     pip3 --no-cache-dir install 'mako' 'pyzmq' 'lxml' && \
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

USER buildbot

WORKDIR /buildbot

CMD ["/usr/local/bin/dumb-init", "twistd", "-ny", "buildbot.tac"]
