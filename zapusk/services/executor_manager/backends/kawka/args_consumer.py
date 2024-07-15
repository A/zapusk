import os
import logging
from datetime import datetime
import subprocess


from zapusk.kawka import Consumer
from zapusk.models import Job

logger = logging.getLogger(__name__)


class ArgsConsumer(Consumer):
    def process(self, job: Job):
        logger.info(f"{self}: received a job {job} to get args for")

        sink = (self.context or {})["sink"]

        if not job.args_command:
            sink.add(job)
            return

        command = job.args_command
        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ},
            cwd=job.cwd,
        )
        exit_code = proc.wait()
        out, err = proc.communicate()

        if err or exit_code:
            logger.warning(f"{exit_code}: {str(err, 'utf-8')}")
            job.state = Job.JOB_STATE_ENUM.FAILED
            job.updated_at = datetime.now()
            return

        arguments = str(out, "utf-8").split()
        logger.info(f"{self} recieved arguments for a job {job}: {arguments}")
        job.args = arguments
        sink.add(job)
        return
