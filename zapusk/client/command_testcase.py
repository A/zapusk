from unittest import TestCase
from unittest.mock import MagicMock
from zapusk.client.api_client import ApiClient
from testfixtures import TempDirectory

from zapusk.services.config.service import ConfigService

from .output import Output
from .command_manager import CommandManager


CONFIG_DATA = ""


class CommandTestCase(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TempDirectory()
        self.config_file = self.temp_dir / "config.yml"
        self.config_file.write_text(CONFIG_DATA)
        self.config_service = ConfigService(
            config_path=f"{self.temp_dir.path}/config.yml"
        )

        self.printer = MagicMock()
        self.output = Output(
            printer=self.printer,
        )
        self.api_client = ApiClient(base_url="http://example.com")

        self.command_manager = CommandManager(
            output=self.output,
            api_client=self.api_client,
            colors=False,
            config_service=self.config_service,
        )
        return super().setUp()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        self.printer.reset_mock()
        return super().tearDown()
