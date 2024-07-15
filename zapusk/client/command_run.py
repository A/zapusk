from .api_client import ApiClientError
from .command import Command


class CommandRun(Command):
    def run(
        self,
        job_config_id: str,
    ):
        try:
            created_job = self.api_client.create_job(
                {
                    "job_config_id": job_config_id,
                }
            )
            self.print_json(created_job)
        except ApiClientError as ex:
            self.print_error(ex)
