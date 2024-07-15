from .api_client import ApiClientError
from .command import Command


class CommandConfigGroups(Command):
    def run(self):
        try:
            config_groups = self.api_client.get_config_groups()
            self.print_json(config_groups)
        except ApiClientError as ex:
            self.print_error(ex)
