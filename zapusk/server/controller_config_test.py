from unittest import TestCase

from flask import json
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
  - id: sequential
    parallel: 1
  - id: parallel
    parallel: 2

jobs:
    - id: test1
      name: Test1
      command: test1
    - id: test2
      name: Test2
      command: test2
"""


class TestConfigController(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TempDirectory()
        config_file = self.temp_dir / "config.yml"
        config_file.write_text(CONFIG_DATA)

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

    def test_config_groups_list(self):
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
                    },
                ]
            },
        )
