from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os
from typing import Optional

from .id_field import IdField
from .job_config import JobConfig
from .job_group import JobGroup


class JOB_STATE_ENUM(str, Enum):
    """
    Enum contains possible job states
    """

    PENDING = "PENDING"
    """
    Job is added, but hasn't been picked up by any consumer yet.
    """

    RUNNING = "RUNNING"
    """
    Job has been picked up by a consumer.
    """

    FINISHED = "FINISHED"
    """
    Job has been finished with zero exit code.
    """

    FAILED = "FAILED"
    """
    Job has been finished with non-zero exit code.
    """

    CANCELLED = "CANCELLED"
    """
    Job has been cancelled before completion
    """


@dataclass
class Job:
    """
    Job model
    """

    JOB_STATE_ENUM = JOB_STATE_ENUM

    def __str__(self):
        return f"job.{self.job_config_id}.{self.id}"

    @staticmethod
    def from_config(group_config: JobGroup, config: JobConfig):
        """
        returns a new JobItem created from JobConfig object
        """
        return Job(
            group_config=group_config,
            command=config.command,
            args_command=config.args_command,
            group=config.group,
            job_config_id=config.id,
            name=config.name,
            on_finish=config.on_finish,
            on_fail=config.on_fail,
            cwd=config.cwd,
        )

    group_config: JobGroup
    """
    Contains jobconfig for job started with it
    """

    command: str
    """
    A shell command to be executed when job becomes `RUNNING`.
    """

    name: str
    """
    Job human-readable name
    """

    group: str = "default"
    """
    job_group id
    """

    cwd: str = field(default_factory=lambda: os.environ["HOME"])
    """
    current working dir
    """

    job_config_id: Optional[str] = None
    """
    job_config id
    """

    args_command: Optional[str] = None
    """
    A command to get arguments to execute job with
    """

    args: list[str] = field(default_factory=list)

    id: int = field(default_factory=lambda: IdField.next("job_item"))
    """
    Unique Job id generated when it's created
    """

    on_finish: Optional[str] = None
    """
    A command to execute after job has been successfuly finished
    """

    on_fail: Optional[str] = None
    """
    A command to execute after job has been successfuly finished
    """

    state: JOB_STATE_ENUM = JOB_STATE_ENUM.PENDING
    """
    defines current state in the pipeline, such as `PENDING`, `RUNNING`, `FAILED` or `FINISHED`.
    """

    pid: int | None = None
    """
    contains Job process PID if job has been started.
    """

    log: str | None = None
    """
    contains a logfile path if job has been started.
    """

    exit_code: int | None = None
    """
    contains an exit status if job has been finished.
    """

    consumed_by: str | None = None
    """
    Identifier of a consumer took this job
    """

    created_at: datetime = field(default_factory=lambda: datetime.now())
    """
    when job has been added to the WorkLog
    """

    updated_at: datetime = field(default_factory=lambda: datetime.now())
    """
    when job has progressed within the pipeline last time
    """
