from __future__ import annotations
from typing import TYPE_CHECKING
from requests.exceptions import ConnectionError

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

    def handle_error(self, ex):
        if type(ex) ==ApiClientError:
            self.print_error(ex)
            return

        if type(ex) == ConnectionError:
            if "Connection refused by Responses" not in str(ex):
                self.print_error(ApiClientError("Can not connect to the server. Please start server with `zapusk-server`"))
                return

        raise ex



