# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    author: Unknown (!UNKNOWN)
    name: yaml
    type: stdout
    short_description: YAML-ized Ansible screen output, modified by Kieran Gee
    description:
        - Ansible output that can be quite a bit easier to read than the
          default JSON formatting.
    extends_documentation_fragment:
      - default_callback
    requirements:
      - set as stdout in configuration
"""

import yaml
import json
import re
import string

from ansible.module_utils.common.text.converters import to_text
from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.plugins.callback import strip_internal_keys, module_response_deepcopy
from ansible.plugins.callback.default import CallbackModule as Default

# from ansible.plugins.callback import CallbackBase
from ansible.playbook.task_include import TaskInclude
from ansible import constants as C


# from http://stackoverflow.com/a/15423007/115478
def should_use_block(value):
    """Returns true if string should be in block format"""
    for c in "\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


class MyDumper(AnsibleDumper):
    def represent_scalar(self, tag, value, style=None):
        """Uses block style for multi-line strings"""
        if style is None:
            if should_use_block(value):
                style = "|"
                # we care more about readable than accuracy, so...
                # ...no trailing space
                value = value.rstrip()
                # ...and non-printable characters
                value = "".join(
                    x for x in value if x in string.printable or ord(x) >= 0xA0
                )
                # ...tabs prevent blocks from expanding
                value = value.expandtabs()
                # ...and odd bits of whitespace
                value = re.sub(r"[\x0b\x0c\r]", "", value)
                # ...as does trailing space
                value = re.sub(r" +\n", "\n", value)
            else:
                style = self.default_style
        node = yaml.representer.ScalarNode(tag, value, style=style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        return node


class CallbackModule(Default):
    """
    Variation of the Default output which uses nicely readable YAML instead
    of JSON for printing results.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "telethon.general.yamlmod"  # Not a real collection yet...

    def __init__(self):
        super(CallbackModule, self).__init__()

    def __truncate_item(self, item):  # Added by Kieran
        truncated_warning = "... TRUNCATED ⚠ "
        max_message_length = self._display.columns - len(truncated_warning)

        shorter_item = str(item)[:max_message_length]
        if len(shorter_item) >= max_message_length:
            shorter_item += truncated_warning
        return shorter_item

    def v2_runner_item_on_ok(self, result):  # Added by Kieran
        host_label = self.host_label(result)
        if isinstance(result._task, TaskInclude):
            return
        elif result._result.get("changed", False):
            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            msg = "changed"
            color = C.COLOR_CHANGED
        else:
            if not self.get_option("display_ok_hosts"):
                return

            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            msg = "ok"
            color = C.COLOR_OK

        msg = "%s: [%s] => (item=%s)" % (
            msg,
            host_label,
            self._get_item_label(result._result),
        )
        msg = self.__truncate_item(msg)
        self._clean_results(result._result, result._task.action)
        if self._run_is_verbose(result):
            msg += " => %s" % self._dump_results(result._result)
        self._display.display(msg, color=color)

    def v2_runner_item_on_skipped(self, result):  # Added by Kieran
        if self.get_option("display_skipped_hosts"):
            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            self._clean_results(result._result, result._task.action)

            msg = "skipping: [%s] => (item=%s) " % (
                result._host.get_name(),
                self._get_item_label(result._result),
            )
            msg = self.__truncate_item(msg)
            if self._run_is_verbose(result):
                msg += " => %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_SKIP)

    def v2_runner_item_on_failed(self, result):  # Added by Kieran
        if self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        host_label = self.host_label(result)
        self._clean_results(result._result, result._task.action)
        self._handle_exception(
            result._result, use_stderr=self.get_option("display_failed_stderr")
        )

        msg = "failed: [%s]" % (host_label,)
        self._handle_warnings(result._result)
        msg = self.__truncate_item(msg)
        self._display.display(
            msg
            + " (item=%s) => %s"
            % (
                self._get_item_label(result._result),
                self._dump_results(result._result),
            ),
            color=C.COLOR_ERROR,
            stderr=self.get_option("display_failed_stderr"),
        )

    # Below should be all original -------------------------------------------------------------------

    def _dump_results(self, result, indent=None, sort_keys=True, keep_invocation=False):
        if result.get("_ansible_no_log", False):
            return json.dumps(
                dict(
                    censored="The output has been hidden due to the fact that 'no_log: true' was specified for this result"
                )
            )

        # All result keys stating with _ansible_ are internal, so remove them from the result before we output anything.
        abridged_result = strip_internal_keys(module_response_deepcopy(result))

        # remove invocation unless specifically wanting it
        if (
            not keep_invocation
            and self._display.verbosity < 3
            and "invocation" in result
        ):
            del abridged_result["invocation"]

        # remove diff information from screen output
        if self._display.verbosity < 3 and "diff" in result:
            del abridged_result["diff"]

        # remove exception from screen output
        if "exception" in abridged_result:
            del abridged_result["exception"]

        dumped = ""

        # put changed and skipped into a header line
        if "changed" in abridged_result:
            dumped += "changed=" + str(abridged_result["changed"]).lower() + " "
            del abridged_result["changed"]

        if "skipped" in abridged_result:
            dumped += "skipped=" + str(abridged_result["skipped"]).lower() + " "
            del abridged_result["skipped"]

        # if we already have stdout, we don't need stdout_lines
        if "stdout" in abridged_result and "stdout_lines" in abridged_result:
            abridged_result["stdout_lines"] = "<omitted>"

        # if we already have stderr, we don't need stderr_lines
        if "stderr" in abridged_result and "stderr_lines" in abridged_result:
            abridged_result["stderr_lines"] = "<omitted>"

        if abridged_result:
            dumped += "\n"
            dumped += to_text(
                yaml.dump(
                    abridged_result,
                    allow_unicode=True,
                    width=1000,
                    Dumper=MyDumper,
                    default_flow_style=False,
                )
            )

        # indent by a couple of spaces
        dumped = "\n  ".join(dumped.split("\n")).rstrip()
        return dumped

    def _serialize_diff(self, diff):
        return to_text(
            yaml.dump(
                diff,
                allow_unicode=True,
                width=1000,
                Dumper=AnsibleDumper,
                default_flow_style=False,
            )
        )
