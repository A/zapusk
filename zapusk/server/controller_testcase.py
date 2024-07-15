from unittest import TestCase
from testfixtures import Replacer, TempDirectory

from zapusk.services import (
    ConfigService,
    SchedulerService,
    ExecutorManagerService,
    ExecutorManagerKawkaBackend,
)

from .api import create_app


class ControllerTestCase(TestCase):
    maxDiff = None
    config_data = ""

    def before_create_services(self): ...

    def setUp(self) -> None:
        self.replace = Replacer()

        self.temp_dir = TempDirectory()
        self.config_file = self.temp_dir / "config.yml"
        self.config_file.write_text(self.config_data)

        self.before_create_services()

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
        self.replace.restore()

    def write_config(self, data):
        self.config_file.write_text(data)

    def replace_in_environ(self, key, value):
        self.replace.in_environ(key, value)
