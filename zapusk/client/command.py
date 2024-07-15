from __future__ import annotations
from typing import TYPE_CHECKING

from .api_client import ApiClient, ApiClientError
from .output import Output

if TYPE_CHECKING:  # pragma: no cover
    from .command_manager import CommandManager


class Command:
    def __init__(
        self,
        manager: CommandManager,
        api_client: ApiClient,
        output: Output,
        colors=False,
    ) -> None:
        self.api_client = api_client
        self.colors = colors
        self.output = output
        self.manager = manager

    def run(self, *args, **kwargs): ...  # pragma: no cover

    def print_json(self, json_data, one_line=False):
        self.output.json(json_data, colors=self.colors, one_line=one_line)

    def print_error(self, exception):
        self.output.error(exception, colors=self.colors)
