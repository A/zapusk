from .api_client import ApiClientError
from .command import Command


class CommandCancel(Command):
    def run(self, job_id: str | int, scheduled: bool = False):
        try:
            if scheduled:
                cancelled_job = self.api_client.cancel_scheduled_job(job_id)
                self.print_json(cancelled_job)
                return

            cancelled_job = self.api_client.cancel_job(job_id)
            self.print_json(cancelled_job)

        except ApiClientError as ex:
            self.print_error(ex)
