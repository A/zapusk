import json
from unittest.mock import ANY, patch

from .controller_testcase import ControllerTestCase

CONFIG_DATA = """
jobs:
    - name: Echo
      id: scheduled_echo
      command: echo 1
      schedule: "0 0 * 1 *"
"""


class TestSchedulerJobController(ControllerTestCase):
    def before_create_services(self):
        self.write_config(CONFIG_DATA)
        self.replace_in_environ("HOME", self.temp_dir.path)

    def test_controller_scheduled_jobs_list(self):
        res = self.test_client.get("/scheduled-jobs/")
        data = json.loads(res.data)

        self.assertEqual(
            data,
            {
                "data": [
                    {
                        "args_command": None,
                        "command": "echo 1",
                        "cwd": self.temp_dir.path,
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

    def test_controller_scheduled_jobs_create(self):
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
                    "cwd": self.temp_dir.path,
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

    def test_controller_scheduled_jobs_cancel(self):
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

    def test_controller_scheduled_jobs_create_without_command(self):
        res = self.test_client.post(
            "/scheduled-jobs/",
            json={
                "schedule": "1 * * * *",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status, "400 BAD REQUEST")
        self.assertEqual(data, {"error": "Request body contains no `command`"})

    def test_controller_scheduled_jobs_create_without_schedule(self):
        res = self.test_client.post(
            "/scheduled-jobs/",
            json={
                "command": "echo 420",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status, "400 BAD REQUEST")
        self.assertEqual(data, {"error": "Request body contains no `schedule`"})

    def test_controller_scheduled_jobs_create_with_unknown_group(self):
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

    def test_controller_scheduled_jobs_create_failed_by_scheduler_service(self):
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
