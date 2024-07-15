import sys
from time import sleep
from sh import tail

from .api_client import ApiClientError
from .command import Command


class CommandTail(Command):
    def run(self, job_id):
        try:
            job = self.api_client.get_job(job_id)
            while not job["log"]:
                sleep(1)
                job = self.api_client.get_job(job_id)

            for line in tail("-f", "-n", "+1", job["log"], _iter=True):
                self.output.text(line, end="")
        except KeyboardInterrupt:  # pragma: no cover
            self.output.text("Tail has been closed")
            sys.exit(0)
        except ApiClientError as ex:
            self.print_error(ex)
