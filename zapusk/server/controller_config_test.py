import json

from .controller_testcase import ControllerTestCase


CONFIG_DATA = """
job_groups:
  - id: default
    parallel: 10
  - id: sequential
    parallel: 1
  - id: parallel
    parallel: 2

jobs:
    - id: test1
      name: Test1
      command: test1
      cwd: /home/
    - id: test2
      name: Test2
      command: test2
"""


class TestConfigController(ControllerTestCase):
    def test_config_groups_list(self):
        self.write_config(CONFIG_DATA)
        res = self.test_client.get("/config/groups/")
        data = json.loads(res.data)
        self.assertEqual(
            data,
            {
                "data": [
                    {
                        "id": "default",
                        "on_fail": None,
                        "on_finish": None,
                        "parallel": 10,
                    },
                    {
                        "id": "sequential",
                        "on_fail": None,
                        "on_finish": None,
                        "parallel": 1,
                    },
                    {
                        "id": "parallel",
                        "on_fail": None,
                        "on_finish": None,
                        "parallel": 2,
                    },
                ]
            },
        )

    def test_config_jobs_list(self):
        self.write_config(CONFIG_DATA)
        self.replace_in_environ("HOME", "/home/kanye")
        res = self.test_client.get("/config/jobs/")
        data = json.loads(res.data)
        self.assertEqual(
            data,
            {
                "data": [
                    {
                        "args_command": None,
                        "command": "test1",
                        "group": "default",
                        "id": "test1",
                        "name": "Test1",
                        "on_fail": None,
                        "on_finish": None,
                        "schedule": None,
                        "cwd": "/home/",
                    },
                    {
                        "args_command": None,
                        "command": "test2",
                        "group": "default",
                        "id": "test2",
                        "name": "Test2",
                        "on_fail": None,
                        "on_finish": None,
                        "schedule": None,
                        "cwd": "/home/kanye",
                    },
                ]
            },
        )
