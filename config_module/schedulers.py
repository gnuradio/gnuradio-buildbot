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

from buildbot.plugins import util
from buildbot.plugins import schedulers


def get(builders):
    scheds = []
    # pull request scheduler
    scheds.append(
        schedulers.AnyBranchScheduler(
            name="gr_pull_request_handler",
            change_filter=util.ChangeFilter(category='pull', project="gnuradio/gnuradio"),
            treeStableTimer=None,
            builderNames=[b.name for b in builders
                          if "control" in b.tags
                          and "gnuradio" in b.tags
                          and "pull" in b.tags]
        ))
    scheds.append(
        schedulers.AnyBranchScheduler(
            name="volk_pull_request_handler",
            change_filter=util.ChangeFilter(category='pull', project="gnuradio/volk"),
            treeStableTimer=None,
            builderNames=[b.name for b in builders
                          if "control" in b.tags
                          and "volk" in b.tags
                          and "pull" in b.tags]
        ))

    # push event scheduler
    def filter_for_push(change):
        event = change.properties.getProperty("event")
        project = change.properties.getProperty("project")
        if event == "push":
            return True
        return False

    scheds.append(
        schedulers.AnyBranchScheduler(
            name="commit_push_handler",
            change_filter=util.ChangeFilter(filter_fn=filter_for_push, project="gnuradio/gnuradio"),
            treeStableTimer=60,
            builderNames=[b.name for b in builders
                          if "control" in b.tags and "push" in b.tags]
        ))

    scheds.append(
        schedulers.ForceScheduler(
            name="force_pullrequest",
            builderNames=["pull_request_runner"],
            properties=[
                util.StringParameter(
                    name="github.number",
                    label="GitHub pull request number",
                    default="", size=80
                ),
                util.StringParameter(
                    name="github.base.ref",
                    label="pull request base branch",
                    default="master", size=80)
            ],
            codebases=[
                util.CodebaseParameter(
                    "",
                    project=util.FixedParameter(name="project", default="gnuradio/gnuradio"),
                    repository=util.FixedParameter(name="repository", default="https://github.com/gnuradio/gnuradio.git"),
                    branch=util.StringParameter(
                        name="branch",
                        label="pull request branch",
                        default="refs/pull/<PR#>/merge", size=80
                    ),
                    revision=util.FixedParameter(name="revision", default="")
                )
            ]
        ))
    scheds.append(
        schedulers.ForceScheduler(
            name="force_build",
            builderNames=["repo_push_runner"],
            codebases=[
                util.CodebaseParameter(
                    "",
                    project=util.FixedParameter(name="project", default="gnuradio/gnuradio"),
                    repository=util.FixedParameter(name="repository", default="https://github.com/gnuradio/gnuradio.git"),
                )
            ]
        )
    )

    scheds.append(
        schedulers.ForceScheduler(
            name="force_weekly",
            builderNames=["weekly_runner"],
            codebases=[
                util.CodebaseParameter(
                    "",
                    project=util.FixedParameter(name="project", default="gnuradio/gnuradio"),
                    repository=util.FixedParameter(name="repository", default="https://github.com/gnuradio/gnuradio.git"),
                    branch=util.StringParameter(
                        name="branch",
                        label="test branch",
                        default="maint", size=80
                    ),
                    revision=util.FixedParameter(name="revision", default="")
                )
            ])
    )

    scheds.append(
        schedulers.Nightly(
            name="timed_weekly",
            builderNames=["weekly_runner"],
            codebases={
                "":{
                    "repository":"https://github.com/gnuradio/gnuradio.git",
                    "branch": "master",
                    "revision": "None"
                }
            },
            dayOfWeek=[0, 4],
            hour=4,
            minute=0))
    scheds.extend(
        [schedulers.Triggerable(
            name="trigger_" + b.name.lstrip("build_"),
            builderNames=[b.name]
        ) for b in builders if "build" in b.tags]
    )

    scheds.extend(
        [schedulers.Triggerable(
            name="trigger_" + b.name.lstrip("test_"),
            builderNames=[b.name]
        ) for b in builders if "test" in b.tags]
    )
    return scheds
