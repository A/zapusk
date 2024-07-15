import json
from unittest import TestCase
from unittest.mock import ANY, patch

from testfixtures import TempDirectory

from zapusk.services import (
    ConfigService,
    SchedulerService,
    ExecutorManagerService,
    ExecutorManagerKawkaBackend,
)

from .api import create_app

CONFIG_DATA = """
jobs:
    - name: Echo
      id: scheduled_echo
      command: echo 1
      schedule: "0 0 * 1 *"
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

    def test_list(self):
        res = self.test_client.get("/scheduled-jobs/")
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": [
                    {
                        "args_command": None,
                        "command": "echo 1",
                        "group": "default",
                        "id": "scheduled_echo",
                        "name": "Echo",
                        "on_fail": None,
                        "on_finish": None,
                        "schedule": "0 0 * 1 *",
                    }
                ]
            },
        )

    def test_create(self):
        res = self.test_client.post(
            "/scheduled-jobs/",
            json={
                "command": "echo 42",
                "name": "echo",
                "schedule": "1 * * * *",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": {
                    "args_command": None,
                    "command": "echo 42",
                    "group": "default",
                    "id": "scheduled.1",
                    "name": "echo",
                    "on_fail": None,
                    "on_finish": None,
                    "schedule": "1 * * * *",
                }
            },
        )

    def test_cancel(self):
        res = self.test_client.delete(
            "/scheduled-jobs/scheduled_echo",
            json={
                "command": "echo 42",
                "name": "echo",
                "schedule": "1 * * * *",
            },
        )
        data = json.loads(res.data)
        self.assertEqual(data, {"data": True})

        res = self.test_client.get("/scheduled-jobs/")
        data = json.loads(res.data)

        self.assertEqual(data, {"data": []})

    def test_create_without_command(self):
        res = self.test_client.post(
            "/scheduled-jobs/",
            json={
                "schedule": "1 * * * *",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status, "400 BAD REQUEST")
        self.assertEqual(data, {"error": "Request body contains no `command`"})

    def test_create_without_schedule(self):
        res = self.test_client.post(
            "/scheduled-jobs/",
            json={
                "command": "echo 420",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status, "400 BAD REQUEST")
        self.assertEqual(data, {"error": "Request body contains no `schedule`"})

    def test_create_with_unknown_group(self):
        res = self.test_client.post(
            "/scheduled-jobs/",
            json={
                "command": "echo 420",
                "schedule": "1 * * * *",
                "group_id": "unknown",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status, "404 NOT FOUND")
        self.assertEqual(data, {"error": "Unknown group `unknown`"})

    def test_create_failed_by_scheduler_service(self):
        with patch.object(self.scheduler_service, "add", return_value=False):
            res = self.test_client.post(
                "/scheduled-jobs/",
                json={
                    "command": "echo 420",
                    "schedule": "1 * * * *",
                },
            )
            data = json.loads(res.data)

            self.assertEqual(res.status, "500 INTERNAL SERVER ERROR")
            self.assertEqual(data, {"error": "Scheduled job hasn't been added"})
