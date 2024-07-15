import os
import signal
from datetime import datetime
from time import sleep

from zapusk.kawka import ConsumerGroup, Producer
from zapusk.models import Job

from .consumer import ExecutorManagerConsumer


class ExecutorManagerKawkaBackend:
    def start(self):
        self._producer = Producer(name="executor_manager_producer")
        self._consumer = ConsumerGroup(
            producer=self._producer,
            Consumer=ExecutorManagerConsumer,
            parallel=1,
            name="executor_manager",
        )
        self._consumer.start()
        sleep(0.1)

    def add(self, job_item: Job) -> Job:
        self._producer.add(job_item)
        return job_item

    def list(self) -> list[Job]:
        return list(self._producer.all(block=False))

    def get(self, job_id: int) -> Job | None:
        for job_item in self.list():
            if job_item.id != job_id:
                continue
            return job_item
        return None

    def cancel(self, job_item: Job) -> Job:
        if job_item.state in [
            Job.JOB_STATE_ENUM.PENDING,
            Job.JOB_STATE_ENUM.RUNNING,
        ]:
            job_item.state = Job.JOB_STATE_ENUM.CANCELLED
            job_item.updated_at = datetime.now()
            if job_item.pid:
                os.kill(job_item.pid, signal.SIGTERM)

        return job_item

    def terminate(self):
        self._producer.add(Producer.End)
        sleep(1)
        self._consumer.join(1)
