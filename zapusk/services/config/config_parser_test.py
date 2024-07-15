import pytest
from testfixtures import Replacer
import yaml

from zapusk.services.config.constants import DEFAULT_COLORS

from .config_parser import DEFAULT_JOB_GROUPS, DEFAULT_PORT, ConfigParser


@pytest.mark.parametrize(
    "config_yaml,expected_result",
    [
        [
            """

            """,
            {
                "port": DEFAULT_PORT,
                "colors": DEFAULT_COLORS,
                "job_groups": DEFAULT_JOB_GROUPS,
                "jobs": {},
            },
        ],
        [
            """
jobs:
  - name: Sleep Timer
    id: sleep
    command: sleep 10
            """,
            {
                "port": DEFAULT_PORT,
                "colors": DEFAULT_COLORS,
                "job_groups": DEFAULT_JOB_GROUPS,
                "jobs": {
                    "sleep": {
                        "name": "Sleep Timer",
                        "id": "sleep",
                        "command": "sleep 10",
                        "cwd": "/home/",
                        "group": "default",
                        "args_command": None,
                    }
                },
            },
        ],
        [
            """
job_groups:
    - id: awesome_group
      parallel: 4200
jobs:
  - name: Sleep Timer
    group: awesome_group
    id: sleep
    command: sleep 10
            """,
            {
                "port": DEFAULT_PORT,
                "colors": DEFAULT_COLORS,
                "job_groups": {
                    **DEFAULT_JOB_GROUPS,
                    **{
                        "awesome_group": {
                            "id": "awesome_group",
                            "parallel": 4200,
                        },
                    },
                },
                "jobs": {
                    "sleep": {
                        "name": "Sleep Timer",
                        "id": "sleep",
                        "command": "sleep 10",
                        "cwd": "/home/",
                        "group": "awesome_group",
                        "args_command": None,
                    }
                },
            },
        ],
        [
            """
port: 1234
colors: True
job_groups:
    - id: default
      parallel: 1
            """,
            {
                "port": 1234,
                "colors": True,
                "job_groups": {"default": {"id": "default", "parallel": 1}},
                "jobs": {},
            },
        ],
        [
            """
job_groups:
    - id: default
      parallel: 1
      on_fail: echo fail
      on_finish: echo finish

jobs:
  - name: Sleep Timer
    id: sleep
    command: sleep 10
    on_fail: echo job_fail
    on_finish: echo job_finish
            """,
            {
                "port": DEFAULT_PORT,
                "colors": DEFAULT_COLORS,
                "job_groups": {
                    "default": {
                        "id": "default",
                        "parallel": 1,
                        "on_fail": "echo fail",
                        "on_finish": "echo finish",
                    }
                },
                "jobs": {
                    "sleep": {
                        "name": "Sleep Timer",
                        "id": "sleep",
                        "command": "sleep 10",
                        "cwd": "/home/",
                        "group": "default",
                        "args_command": None,
                        "on_fail": "echo job_fail",
                        "on_finish": "echo job_finish",
                    }
                },
            },
        ],
        [
            """
job_groups:
    - id: default
      parallel: 1

jobs:
  - name: Sleep Timer
    id: sleep
    command: sleep 10
    unknown_property: 1
            """,
            {
                "port": DEFAULT_PORT,
                "colors": DEFAULT_COLORS,
                "job_groups": {
                    "default": {
                        "id": "default",
                        "parallel": 1,
                    }
                },
                "jobs": {
                    "sleep": {
                        "name": "Sleep Timer",
                        "id": "sleep",
                        "command": "sleep 10",
                        "cwd": "/home/",
                        "group": "default",
                        "args_command": None,
                    }
                },
            },
        ],
    ],
    ids=[
        "default_config",
        "job_config",
        "jobgroups_and_jobs",
        "port_and_override_default_jobgroup",
        "callbacks",
        "unknown_property",
    ],
)
def test_config_parser_should_parse_config(config_yaml, expected_result):
    replace = Replacer()
    replace.in_environ("HOME", "/home/")

    config_parser = ConfigParser()
    config_data = yaml.safe_load(config_yaml)
    res = config_parser.parse(config_data)

    assert res == expected_result
    replace.restore()


####################################


@pytest.mark.parametrize(
    "config_yaml,expection_msg",
    [
        [
            """
# Should fail with unknown group id
jobs:
  - name: Sleep Timer
    group: awesome_group
    id: sleep
    command: sleep 10
            """,
            "Unknown job_group `awesome_group` in job_config.sleep",
        ],
        [
            """
# Should fail with parallel config error
job_groups:
    - id: awesome_group
      parallel: -1
            """,
            "`parallel` must be a positive number",
        ],
    ],
    ids=["unknown_id_fail", "negative_parallel_fail"],
)
def test_job_should_fail_parsing_config(config_yaml, expection_msg):
    config_parser = ConfigParser()
    config_data = yaml.safe_load(config_yaml)

    try:
        config_parser.parse(config_data)
        raise Exception("Should fail")
    except Exception as ex:
        assert ex.args[0] == expection_msg
