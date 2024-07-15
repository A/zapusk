from unittest import TestCase
from unittest.mock import MagicMock
from zapusk.client.api_client import ApiClient

from .output import Output
from .command_manager import CommandManager


class CommandTestCase(TestCase):
    def setUp(self) -> None:
        self.printer = MagicMock()
        self.output = Output(
            printer=self.printer,
        )
        self.api_client = ApiClient(base_url="http://example.com")

        self.command_manager = CommandManager(
            output=self.output,
            api_client=self.api_client,
            colors=False,
        )
        return super().setUp()

    def tearDown(self) -> None:
        self.printer.reset_mock()
        return super().tearDown()
