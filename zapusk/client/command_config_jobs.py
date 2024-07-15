from .api_client import ApiClientError
from .command import Command


class CommandConfigJobs(Command):
    def run(self):
        try:
            config_jobs = self.api_client.get_config_jobs()
            self.print_json(config_jobs)
        except ApiClientError as ex:
            self.print_error(ex)
