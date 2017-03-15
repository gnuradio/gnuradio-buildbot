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

from six import iteritems
import copy
import os


def join_dicts(old_dict, new_dict):
    """
    This function joins new values from a new_dict into an older dict
     - dicts will be updated
     - lists will be appended
     - unavailable keys will be added
     - existing entries (not list or dicts) will raise an error
    """
    for k, v in iteritems(new_dict):
        old_v = old_dict.get(k, None)
        if old_v is None:
            old_dict.update({k: v})
        elif type(old_v) is not type(v):
            raise Exception("dicts have mismatching value type")
        elif isinstance(v, dict):
            new_v = {}
            new_v.update(old_v)
            new_v.update(v)
            old_dict.update({k: new_v})
        elif isinstance(v, list):
            old_dict.update({k: old_v + v})
        else:
            raise Exception("entry {} is already in the dict and not a dict or list".format(
                k))


class BuildTrigger(steps.Trigger):
    renderables = ["src_base"]

    def __init__(self,
                 src_base="/tmp/src",
                 build_config=None,
                 runner="pull",
                 test_merge=True,
                 **kwargs):
        """
        branch_config is a dict with the key branches
        listing the test branches in ascending order
        and branch names as key with a list of important merges
        """
        if build_config is None:
            raise Exception("build_config must contain build definition")
        self.build_config = build_config
        self.test_branches = self.build_config.get("builders").keys()
        self.test_merge = test_merge
        self.src_base = src_base
        self.runner = runner
        super(BuildTrigger, self).__init__(**kwargs)

    def getSchedulersAndProperties(self):
        """
        """
        scheds = []
        for branch in self.test_branches:
            branch_config = self.build_config["builders"][branch]
            # only test this if we want to test for merges
            if self.test_merge and self.build.getProperty("merge_" + branch):
                bases = branch_config.get("bases", None)
                if (bases is not None
                        and self.set_properties.get("pr_base", "") not in bases
                        and self.build.getProperty("branch", "") not in bases):
                    continue
            else:
                # test if the branch to build corresponds
                # to the current branch config
                if not (self.build.getProperty("branch", "") == branch or self.set_properties.get("pr_base", "") == branch):
                    continue
            for build in branch_config.get("builds", ()):
                if self.runner not in build.get("runners", ()):
                    continue
                bases = build.get("bases", None)
                # only test this if we want to test for merges
                if self.test_merge:
                    if (bases is not None
                        and self.set_properties.get(
                            "pr_base", "") not in bases
                        and self.build.getProperty(
                            "branch", "") not in bases):
                        continue

                props = copy.deepcopy(self.set_properties)
                opts = build.get("opts", ())
                build_scheds = build.get("scheds", ())
                join_dicts(props, build.get("properties", {}))
                for opt in opts:
                    join_dicts(props, self.build_config["buildopts"][opt].get(
                        "properties", {}))
                props.update({
                    "virtual_builder_tags":
                    tuple(props.get("virtual_builder_tags", ())) + (branch, ),
                    "status_branch":
                    branch,
                })
                if self.runner == "pull":
                    props.update({
                        "src_dir":
                        os.path.join(props.get("src_dir", ""), branch)
                    })
                for sched in build_scheds:
                    s_props = copy.deepcopy(props)
                    virtual_name = "_".join((sched, ) + tuple(
                        s_props.get("virtual_builder_tags", ())))
                    s_props.update({"virtual_builder_name": virtual_name})
                    scheds.append({
                        "sched_name":
                        "trigger_" + sched,
                        "props_to_set":
                        s_props,
                        "unimportant":
                        not (branch in self.build_config["builders"].get(
                            s_props.get("pr_base", ""), {}).get(
                                "important",
                                ()) or branch == s_props.get("pr_base", "")
                             or branch == self.build.getProperty("branch", ""))
                    })
        return scheds
