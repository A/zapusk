import logging
from zapusk.models import Job

logger = logging.getLogger(__name__)


class ExecutorManagerService:
    """
    JobLog service is a generic interface for a given backend to interact
    with the pipeline
    """

    def __init__(self, backend=None):
        logger.info("Start joblog")

        if not backend:
            raise Exception("ExecutorManagerService backend isn't configured")

        self.__backend = backend
        self.__backend.start()

    def get(self, job_id: int) -> Job | None:
        """
        returns a job by its id
        """
        return self.__backend.get(job_id)

    def list(self) -> list[Job]:
        """
        returns all jobs in the pipeline
        """
        return self.__backend.list()

    def add(self, job_item: Job) -> Job:
        """
        adds a job to the pipeline
        """
        return self.__backend.add(job_item)

    def cancel(self, job_item: Job) -> Job:
        """
        cancels a job
        """
        return self.__backend.cancel(job_item)

    def terminate(self) -> None:
        self.__backend.terminate()
