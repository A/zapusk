import json
from unittest import TestCase
from unittest.mock import ANY

from testfixtures import TempDirectory

from zapusk.server.controller_testcase import ControllerTestCase
from zapusk.services import (
    ConfigService,
    SchedulerService,
    ExecutorManagerService,
    ExecutorManagerKawkaBackend,
)

from .api import create_app

CONFIG_DATA = """
job_groups:
  - id: default
    parallel: 10
  - id: cmd
    parallel: 2

jobs:
    - name: Echo
      id: echo
      command: echo 1
"""


class TestJobController(ControllerTestCase):
    def before_create_services(self):
        self.write_config(CONFIG_DATA)
        self.replace_in_environ("HOME", self.temp_dir.path)

    def test_controller_jobs_create_job(self):
        res = self.test_client.post("/jobs/", json={"job_config_id": "echo"})
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": {
                    "args": [],
                    "args_command": None,
                    "command": "echo 1",
                    "cwd": self.temp_dir.path,
                    "consumed_by": None,
                    "created_at": ANY,
                    "exit_code": None,
                    "group": "default",
                    "group_config": {
                        "id": "default",
                        "on_fail": None,
                        "on_finish": None,
                        "parallel": 10,
                    },
                    "id": ANY,
                    "job_config_id": "echo",
                    "log": None,
                    "name": "Echo",
                    "on_fail": None,
                    "on_finish": None,
                    "pid": None,
                    "state": "PENDING",
                    "updated_at": ANY,
                }
            },
        )

    def test_controller_jobs_create_command(self):
        res = self.test_client.post(
            "/jobs/",
            json={
                "command": "echo 42",
                "group_id": "cmd",
                "name": "test_command",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": {
                    "args": [],
                    "args_command": None,
                    "command": "echo 42",
                    "cwd": self.temp_dir.path,
                    "consumed_by": None,
                    "created_at": ANY,
                    "exit_code": None,
                    "group": "default",
                    "group_config": {
                        "id": "cmd",
                        "on_fail": None,
                        "on_finish": None,
                        "parallel": 2,
                    },
                    "id": ANY,
                    "job_config_id": ANY,
                    "log": None,
                    "name": "test_command",
                    "on_fail": None,
                    "on_finish": None,
                    "pid": None,
                    "state": "PENDING",
                    "updated_at": ANY,
                }
            },
        )

    def test_controller_jobs_get_job(self):
        res = self.test_client.post("/jobs/", json={"job_config_id": "echo"})
        data = json.loads(res.data)

        job_id = data["data"]["id"]
        res = self.test_client.get(f"/jobs/{job_id}")
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": {
                    "args": [],
                    "args_command": None,
                    "command": "echo 1",
                    "cwd": self.temp_dir.path,
                    "consumed_by": None,
                    "created_at": ANY,
                    "exit_code": None,
                    "group": "default",
                    "group_config": {
                        "id": "default",
                        "on_fail": None,
                        "on_finish": None,
                        "parallel": 10,
                    },
                    "id": ANY,
                    "job_config_id": "echo",
                    "log": None,
                    "name": "Echo",
                    "on_fail": None,
                    "on_finish": None,
                    "pid": None,
                    "state": "PENDING",
                    "updated_at": ANY,
                }
            },
        )

    def test_controller_jobs_list_job(self):
        res = self.test_client.post("/jobs/", json={"job_config_id": "echo"})
        data = json.loads(res.data)

        job_id = data["data"]["id"]
        res = self.test_client.get("/jobs/")
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": [
                    {
                        "args": [],
                        "args_command": None,
                        "command": "echo 1",
                        "cwd": self.temp_dir.path,
                        "consumed_by": None,
                        "created_at": ANY,
                        "exit_code": None,
                        "group": "default",
                        "group_config": {
                            "id": "default",
                            "on_fail": None,
                            "on_finish": None,
                            "parallel": 10,
                        },
                        "id": job_id,
                        "job_config_id": "echo",
                        "log": None,
                        "name": "Echo",
                        "on_fail": None,
                        "on_finish": None,
                        "pid": None,
                        "state": "PENDING",
                        "updated_at": ANY,
                    }
                ]
            },
        )

    def test_controller_jobs_cancel_job(self):
        res = self.test_client.post(
            "/jobs/", json={"command": "sleep 60", "name": "test_command"}
        )
        data = json.loads(res.data)

        job_id = data["data"]["id"]
        res = self.test_client.delete(f"/jobs/{job_id}")
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": {
                    "args": [],
                    "args_command": None,
                    "command": "sleep 60",
                    "cwd": self.temp_dir.path,
                    "consumed_by": ANY,
                    "created_at": ANY,
                    "exit_code": None,
                    "group": "default",
                    "group_config": {
                        "id": "default",
                        "on_fail": None,
                        "on_finish": None,
                        "parallel": 10,
                    },
                    "id": ANY,
                    "job_config_id": ANY,
                    "log": ANY,
                    "name": "test_command",
                    "on_fail": None,
                    "on_finish": None,
                    "pid": None,
                    "state": "CANCELLED",
                    "updated_at": ANY,
                }
            },
        )

    def test_controller_jobs_get_unknown(self):
        res = self.test_client.get(f"/jobs/420")
        data = json.loads(res.data)

        self.assertEqual(res.status, "404 NOT FOUND")
        self.assertEqual(data, {"error": "Job with id 420 not found"})

    def test_create_without_body(self):
        res = self.test_client.post(f"/jobs/", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status, "400 BAD REQUEST")
        self.assertEqual(
            data, {"error": "Request body contains no `command` or `job_config_id`"}
        )

    def test_controller_jobs_create_with_unknown_jobgroup(self):
        res = self.test_client.post(
            f"/jobs/",
            json={
                "command": "echo 1",
                "group_id": "unknown",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status, "404 NOT FOUND")
        self.assertEqual(data, {"error": 'group_id "unknown" not found'})

    def test_controller_jobs_create_with_unknown_jobconfig_id(self):
        res = self.test_client.post(
            f"/jobs/",
            json={
                "job_config_id": "unknown",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status, "404 NOT FOUND")
        self.assertEqual(data, {"error": "Job with id `unknown` not found"})

    def test_controller_jobs_cancel_unknown_job(self):
        res = self.test_client.delete("/jobs/420")
        data = json.loads(res.data)

        self.assertEqual(res.status, "404 NOT FOUND")
        self.assertEqual(data, {"error": "Job with id `420` not found"})
