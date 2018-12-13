# Copyright 2017 Andrej Rode
#
# This file is part of gnuradio-buildbot
#
# gnuradio-buildbot is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# gnuradio-buildbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from buildbot.plugins import steps
from buildbot.plugins import util

from config_module import tokens

import os

env = {
    "CCACHE_DIR": util.Interpolate(
        os.path.join("/cache", "%(prop:distro)s", "ccache")
    ),
    "PATH": [util.Property("cov_path", "/usr/local/share/cov-build/bin"), "/usr/lib/ccache/", "/usr/lib64/ccache/", "${PATH}"]
}


def build_coverity():
    remove_build = steps.RemoveDirectory("build")
    remove_src = steps.RemoveDirectory("src")
    create_build = steps.MakeDirectory("build")
    download_src_archive = steps.FileDownload(
        mastersrc=util.Property("src_archive"),
        workerdest="src.tar.xz",
        workdir="src"
    )
    extract_src_archive = steps.ShellCommand(
        name="Extract source archive",
        command=["tar", "xJf", "src.tar.xz"],
        workdir="src"
    )
    cmake_step = steps.CMake(
        path="../src/",
        definitions=util.Property("cmake_defs", {}),
        options=util.Property("cmake_opts", []),
        workdir="build",
        env=env
    )

    make_step = steps.Compile(
        command=["cov-build", "--dir", "cov-int", "make", "-j", "16", "-l", "32"],
        workdir="build",
        env=env
    )

    compress = steps.ShellCommand(
        command=["tar", "czvf", "gnuradio.tgz", "cov-int"],
        workdir="build")

    upload = steps.ShellCommand(
        command=[
            "curl", "--form", "token="+tokens.coverityToken,
            "--form", "email=mail@andrejro.de", "--form", "file=@gnuradio.tgz",
            "--form", util.Interpolate("version=%(prop:revision)s"), "--form",
            util.Interpolate("description=\"Weekly Buildbot submission for %(prop:branch)s branch \""),
            "https://scan.coverity.com/builds?project=GNURadio"
        ],
        workdir="build")

    factory = util.BuildFactory()
    factory.addStep(remove_build)
    factory.addStep(remove_src)
    factory.addStep(create_build)
    factory.addStep(download_src_archive)
    factory.addStep(extract_src_archive)
    factory.addStep(cmake_step)
    factory.addStep(make_step)
    factory.addStep(compress)
    factory.addStep(upload)
    return factory
