from typing import Optional
from zapusk.client.api_client import ApiClient
from zapusk.client.command_tail import CommandTail
from zapusk.services.config.service import ConfigService
from .command_exec import CommandExec
from .command_run import CommandRun
from .command_cancel import CommandCancel
from .command_list import CommandList
from .command_waybar import CommandWaybar
from .command_config_jobs import CommandConfigJobs
from .command_config_groups import CommandConfigGroups
from .output import Output


class CommandManager:
    def __init__(
        self,
        config_service=ConfigService(),
        output=Output(),
        colors=None,
        api_client: Optional[ApiClient] = None,
    ) -> None:
        self.output = output
        self.config_service = config_service
        config = self.config_service.get_config()

        self.api_client = (
            api_client
            if api_client
            else ApiClient(
                base_url=f"http://localhost:{config.port}/",
            )
        )

        self.colors = (
            colors if colors != None else self.config_service.get_config().colors
        )
        kwargs = {
            "colors": self.colors,
            "output": self.output,
            "api_client": self.api_client,
            "manager": self,
        }

        self.exec = CommandExec(**kwargs)
        self.run = CommandRun(**kwargs)
        self.cancel = CommandCancel(**kwargs)
        self.list = CommandList(**kwargs)
        self.waybar = CommandWaybar(**kwargs)
        self.tail = CommandTail(**kwargs)
        self.config_jobs = CommandConfigJobs(**kwargs)
        self.config_groups = CommandConfigGroups(**kwargs)
