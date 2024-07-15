from datetime import datetime, timezone
import logging
from threading import Thread
from time import sleep

from zapusk.models import Job, ScheduledJob
from zapusk.services.config import ConfigService
from zapusk.services.executor_manager import ExecutorManagerService


logger = logging.getLogger(__name__)


class SchedulerService:
    __terminated = False

    def __init__(
        self,
        config_service: ConfigService,
        executor_manager_service: ExecutorManagerService,
        interval: float = 1,
    ) -> None:
        self.__interval = interval
        self.__config_service = config_service if config_service else ConfigService()
        self.__executor_manager_service = executor_manager_service
        self.__scheduled_jobs = [j for j in config_service.list_jobs() if j.schedule]
        logger.info(f"Scheduled jobs detected {[i.id for i in self.__scheduled_jobs]}")

        self.__data: dict[str, ScheduledJob] = {}

    def start(self) -> None:
        """
        Reads config service, schedules jobs and starts the scheduler

        """
        self.add_from_config()
        thread = Thread(target=self.__start_thread)
        thread.start()

    def add(self, job_config):
        """
        Schedule job from JobConfig
        """
        try:
            scheduled_job = ScheduledJob(
                job_config=job_config,
            )
            self.__data[job_config.id] = scheduled_job
            return True
        except ValueError as ex:
            logger.info(ex.args[0])
            return False

    def delete(self, job_config_id):
        """
        Removes given scheduled job by config id
        """
        if job_config_id in self.__data:
            del self.__data[job_config_id]
            return True
        return False

    def list(self):
        """
        list all scheduled job configs
        """
        return [sj.job_config for sj in self.__data.values()]

    def add_from_config(self) -> None:
        """
        Reads config from self.config_service and add schedule all jobs
        """
        for job_config in self.__scheduled_jobs:
            # Just a type guard, was checked in __init__
            if not job_config.schedule:  # pragma: no cover
                continue
            self.add(job_config)

    def terminate(self) -> None:
        self.__terminated = True

    def __start_thread(self) -> None:
        while not self.__terminated:
            now = datetime.now(timezone.utc)
            for scheduled_item in self.__data.values():
                logger.debug(f"Checking schedule for {scheduled_item}")
                logger.debug(
                    f"NEXT:{datetime.fromtimestamp(scheduled_item.next)} < NOW:{now}"
                )
                if scheduled_item.next < now.timestamp():
                    self.__run_job(scheduled_item, now)

            sleep(self.__interval)

    def __run_job(self, scheduled_job: ScheduledJob, now: datetime) -> None:
        job_config = scheduled_job.job_config
        job_group = self.__config_service.get_job_group_or_default(
            job_config.group or "default"
        )

        logger.info(f"Adding a job {scheduled_job.job_config} to the queue")
        scheduled_job.record_run(now)
        self.__executor_manager_service.add(
            Job.from_config(
                group_config=job_group,
                config=job_config,
            )
        )
