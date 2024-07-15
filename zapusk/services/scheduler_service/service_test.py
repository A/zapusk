from time import sleep
from unittest import TestCase
from unittest.mock import patch
from testfixtures import Replacer, TempDirectory, mock_datetime, Replace

from zapusk.models import Job
from zapusk.models.job_config import JobConfig
from zapusk.services import ConfigService

from .service import SchedulerService

CONFIG_DATA = """
jobs:
    - name: Echo
      id: echo
      command: echo 1
      schedule: "30 * * * *"
"""


class MockExecutorManager:
    def add(self):
        pass


class TestSchedulerService(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TempDirectory()
        self.config_file = self.temp_dir / "config.yml"
        self.config_file.write_text(CONFIG_DATA)
        self.config_service = ConfigService(
            config_path=f"{self.temp_dir.path}/config.yml"
        )

        self.executor_manager_service = MockExecutorManager()
        self.d = mock_datetime(1970, 1, 1, 8, 0, 0, delta=0)

        self.r = Replacer()
        self.r.replace("zapusk.services.scheduler_service.service.datetime", self.d)
        self.r.replace("zapusk.models.scheduled_job.datetime", self.d)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        self.r.restore()

    def test_scheduler_service_should_work(self):
        scheduler_service = SchedulerService(
            config_service=self.config_service,
            executor_manager_service=self.executor_manager_service,  # type: ignore
            interval=0.1,
        )

        with patch.object(self.executor_manager_service, "add") as mock:
            self.d.set(1970, 1, 1, 8, 11, 5)
            scheduler_service.start()
            sleep(1)
            self.d.set(1970, 1, 1, 8, 30, 10)
            sleep(1)
            scheduler_service.terminate()

            args = mock.call_args.args

            scheduled_job = args[0]
            self.assertEqual(type(scheduled_job), Job)
            self.assertEqual(scheduled_job.name, "Echo")

    def test_scheduler_service_should_not_add_jobs_without_schedule(self):
        scheduler_service = SchedulerService(
            config_service=self.config_service,
            executor_manager_service=self.executor_manager_service,  # type: ignore
            interval=0.1,
        )

        with patch.object(self.executor_manager_service, "add") as mock:
            scheduler_service.start()
            res = scheduler_service.add(
                JobConfig(id="no_schedule", name="No Schedule", command="echo 1")
            )
            scheduler_service.terminate()
            self.assertEqual(res, False)

    def test_scheduler_service_should_list_all_scheduled_jobs(self):
        scheduler_service = SchedulerService(
            config_service=self.config_service,
            executor_manager_service=self.executor_manager_service,  # type: ignore
        )

        scheduler_service.add(
            JobConfig(
                id="1",
                name="1",
                command="echo 1",
                schedule="1 * * * *",
            )
        )
        scheduler_service.add(
            JobConfig(
                id="2",
                name="2",
                command="echo 2",
                schedule="1 * * * *",
            )
        )

        res = scheduler_service.list()

        self.assertEqual(
            res,
            [
                {
                    "id": "1",
                    "name": "1",
                    "command": "echo 1",
                    "group": "default",
                    "args_command": None,
                    "on_finish": None,
                    "on_fail": None,
                    "schedule": "1 * * * *",
                },
                {
                    "id": "2",
                    "name": "2",
                    "command": "echo 2",
                    "group": "default",
                    "args_command": None,
                    "on_finish": None,
                    "on_fail": None,
                    "schedule": "1 * * * *",
                },
            ],
        )

    def test_scheduler_service_should_delete_scheduled_jobs(self):
        scheduler_service = SchedulerService(
            config_service=self.config_service,
            executor_manager_service=self.executor_manager_service,  # type: ignore
        )

        scheduler_service.add(
            JobConfig(
                id="1",
                name="1",
                command="echo 1",
                schedule="1 * * * *",
            )
        )
        scheduler_service.add(
            JobConfig(
                id="2",
                name="2",
                command="echo 2",
                schedule="1 * * * *",
            )
        )

        scheduler_service.delete("1")
        res = scheduler_service.list()

        self.assertEqual(
            res,
            [
                {
                    "id": "2",
                    "name": "2",
                    "command": "echo 2",
                    "group": "default",
                    "args_command": None,
                    "on_finish": None,
                    "on_fail": None,
                    "schedule": "1 * * * *",
                },
            ],
        )

    def test_scheduler_service_delete_should_ignore_unknown_jobs(self):
        scheduler_service = SchedulerService(
            config_service=self.config_service,
            executor_manager_service=self.executor_manager_service,  # type: ignore
        )

        scheduler_service.add(
            JobConfig(
                id="1",
                name="1",
                command="echo 1",
                schedule="1 * * * *",
            )
        )
        scheduler_service.add(
            JobConfig(
                id="2",
                name="2",
                command="echo 2",
                schedule="1 * * * *",
            )
        )

        res = scheduler_service.delete("3")
        self.assertEqual(res, False)

        res = scheduler_service.list()

        self.assertEqual(
            res,
            [
                {
                    "id": "1",
                    "name": "1",
                    "command": "echo 1",
                    "group": "default",
                    "args_command": None,
                    "on_finish": None,
                    "on_fail": None,
                    "schedule": "1 * * * *",
                },
                {
                    "id": "2",
                    "name": "2",
                    "command": "echo 2",
                    "group": "default",
                    "args_command": None,
                    "on_finish": None,
                    "on_fail": None,
                    "schedule": "1 * * * *",
                },
            ],
        )
