from typing import Any
from zapusk.models.job import JOB_STATE_ENUM

from .api_client import ApiClientError
from .command import Command


class CommandList(Command):
    def run(
        self,
        filter: Any = None,
        scheduled: bool = False,
    ):
        try:
            if scheduled:
                jobs = self.api_client.list_scheduled_jobs()
                self.print_json(jobs)
                return

            jobs = self.api_client.list_jobs()

            if filter and filter != "ALL":
                jobs = [i for i in jobs if i["state"] == filter]

            self.print_json(jobs)
            return

        except Exception as ex:
            self.handle_error(ex)
