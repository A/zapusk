import logging
import subprocess
from time import time
from datetime import datetime

from zapusk.kawka import Consumer
from zapusk.models import Job

logger = logging.getLogger(__name__)


class Executor(Consumer):
    def process(self, job: Job):
        logger.info(f"{self} received a job to run {job}")

        logfile_path = f"/tmp/zapusk-{time()}.log"

        if job.state == Job.JOB_STATE_ENUM.CANCELLED:
            logger.info("Skipping cancelled job {job.id}")
            return

        job.state = Job.JOB_STATE_ENUM.RUNNING
        job.log = logfile_path
        job.consumed_by = self.name
        job.updated_at = datetime.now()
        job.command = " ".join([job.command, *job.args])

        logger.info(f"Run a command {job.command}")

        with open(logfile_path, "w") as logfile:
            proc = subprocess.Popen(
                job.command,
                shell=True,
                stdout=logfile,
                stderr=logfile,
            )
            job.pid = proc.pid

        exit_code = proc.wait()

        job.exit_code = exit_code
        if job.state == Job.JOB_STATE_ENUM.CANCELLED:
            logger.info(f"Job {job.id} has been cancelled")
            return

        if exit_code == 0:
            job.state = Job.JOB_STATE_ENUM.FINISHED
            job.updated_at = datetime.now()
            logger.info(f"{self.name} finished {job} job")

            on_finish = job.on_finish or job.group_config.on_finish
            if on_finish:
                subprocess.Popen(
                    on_finish.format(job=job),
                    shell=True,
                )

        else:
            job.state = Job.JOB_STATE_ENUM.FAILED
            job.updated_at = datetime.now()

            on_fail = job.on_fail or job.group_config.on_fail
            if on_fail:
                subprocess.Popen(
                    on_fail.format(job=job),
                    shell=True,
                )

            logger.info(f"{self.name} failed {job} job")
