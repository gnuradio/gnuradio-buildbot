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

from gnuradio_buildbot import custom_steps

from buildbot.process.results import SUCCESS
from buildbot.process.results import SKIPPED
import json
import os


_BASEPATH = os.environ.get("BUILDBOT_SRC_BASE", "/tmp")
_PUSH_SRC_BASE = os.path.join(_BASEPATH, "push")


def build_push():

    create_src = steps.MakeDirectory(
        name="create src directory",
        dir="src")
    clone_step = steps.GitHub(
        name="fetch PR source",
        repourl=util.Property("repository"),
        mode="full",
        method="fresh",
        submodules=True,
        clobberOnFailure=True,
        getDescription=True,
        workdir="src")

    rm_src_archive = steps.ShellCommand(
        name="remove old source archive",
        command=[
            "rm", "-rf", util.Interpolate(
                os.path.join(_PUSH_SRC_BASE, "%(prop:branch)s"
                             "%(prop:commit-description)s.tar.xz"))
        ],
        workdir="src",
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS)

    create_src_archive = steps.ShellCommand(
        name="create source archive",
        command=[
            "tar", "cJf", util.Interpolate(
                os.path.join(_PUSH_SRC_BASE, "%(prop:branch)s"
                             "%(prop:commit-description)s.tar.xz")), "."
        ],
        workdir="src",
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS,
    )

    set_merge_property = steps.SetProperty(
        property=util.Interpolate("merge_%(prop:branch)s"),
        value=True,
        hideStepIf=True,
    )

    # load builders.json with definitions on how to build things
    parent_path = os.path.dirname(__file__)
    with open(os.path.join(parent_path, "builders.json"), "r") as builders_file:
        build_config = json.loads(builders_file.read())

    # now we have all necessary merge properties together,
    # we can actually kickoff builds for them

    trigger_builds = custom_steps.BuildTrigger(
        name="trigger all builders",
        build_config=build_config,
        schedulerNames=["trigger"],
        runner="push",
        set_properties={
            "src_archive": util.Interpolate(
                os.path.join(_PUSH_SRC_BASE,"%(prop:branch)s","%(prop:commit-description)s.tar.xz"))
        },
        updateSourceStamp=True,
        waitForFinish=True
    )

    factory = util.BuildFactory()
    factory.addStep(create_src)
    factory.addStep(clone_step)
    factory.addStep(rm_src_archive)
    factory.addStep(create_src_archive)
    factory.addStep(set_merge_property)
    factory.addStep(trigger_builds)
    return factory
