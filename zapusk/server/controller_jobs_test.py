import json
from unittest import TestCase
from unittest.mock import ANY

from testfixtures import TempDirectory

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


class TestJobController(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TempDirectory()
        self.config_file = self.temp_dir / "config.yml"
        self.config_file.write_text(CONFIG_DATA)

        self.executor_manager_service = ExecutorManagerService(
            backend=ExecutorManagerKawkaBackend(),
        )
        self.config_service = ConfigService(
            config_path=f"{self.temp_dir.path}/config.yml"
        )
        self.scheduler_service = SchedulerService(
            config_service=self.config_service,
            executor_manager_service=self.executor_manager_service,
        )
        self.scheduler_service.start()

        self.app = create_app(
            executor_manager_service=self.executor_manager_service,
            config_service=self.config_service,
            scheduler_service=self.scheduler_service,
        )
        self.test_client = self.app.test_client()

    def tearDown(self) -> None:
        self.executor_manager_service.terminate()
        self.scheduler_service.terminate()
        self.temp_dir.cleanup()

    def test_create_job(self):
        res = self.test_client.post("/jobs/", json={"job_config_id": "echo"})
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": {
                    "args": [],
                    "args_command": None,
                    "command": "echo 1",
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

    def test_create_command(self):
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

    def test_get_job(self):
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

    def test_list_job(self):
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

    def test_cancel_job(self):
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

    def test_get_unknown(self):
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

    def test_create_with_unknown_jobgroup(self):
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

    def test_create_with_unknown_jobconfig_id(self):
        res = self.test_client.post(
            f"/jobs/",
            json={
                "job_config_id": "unknown",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status, "404 NOT FOUND")
        self.assertEqual(data, {"error": "Job with id `unknown` not found"})

    def test_cancel_unknown_job(self):
        res = self.test_client.delete("/jobs/420")
        data = json.loads(res.data)

        self.assertEqual(res.status, "404 NOT FOUND")
        self.assertEqual(data, {"error": "Job with id `420` not found"})
