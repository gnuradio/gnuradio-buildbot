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
    "PATH": ["/usr/lib/ccache/", "/usr/lib64/ccache/", "${PATH}"]
}


def build_coverage():
    remove_build = steps.RemoveDirectory("build")
    create_build = steps.MakeDirectory("build")
    cmake_step = steps.CMake(
        path=util.Property("src_dir"),
        definitions=util.Property("cmake_defs", {}),
        options=util.Property("cmake_opts", []),
        workdir="build",
        env=env
    )

    @util.renderer
    def join_make_opts(props):
        make_opts = props.getProperty("make_opts", [])
        return ["make"] + make_opts

    make_step = steps.Compile(
        command=join_make_opts,
        workdir="build",
        env=env
    )

    test_coverage = steps.ShellCommand(
        command=["make", "coverage"],
        workdir="build"
    )

    upload_coverage_data = steps.ShellCommand(
        command=[
            "bash", "-c",
            util.Interpolate("bash <(curl -s https://codecov.io/bash) -t "+tokens.codecovToken+" -C %(prop:revision)s -f coverage.info.cleaned")
        ],
        workdir="build"
    )

    factory = util.BuildFactory()
    factory.addStep(remove_build)
    factory.addStep(create_build)
    factory.addStep(cmake_step)
    factory.addStep(make_step)
    factory.addStep(test_coverage)
    factory.addStep(upload_coverage_data)
    return factory
