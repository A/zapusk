from dataclasses import dataclass
from croniter import croniter
from datetime import datetime, timezone
from typing import Optional

from .base_model import BaseModel
from .job_config import JobConfig


@dataclass(eq=False)
class ScheduledJob(BaseModel):
    job_config: JobConfig

    next: int = 0
    """
    Next execution time
    """

    last_run: Optional[datetime] = None
    """
    list time job run
    """

    def __post_init__(self):
        now = datetime.now(timezone.utc)
        if self.job_config.schedule:
            self.__iter = croniter(self.job_config.schedule, start_time=now)
        else:
            raise ValueError(
                "Job config {self.job_config} contains no `schedule` property"
            )

        self.next = self.__iter.get_next(start_time=now)

    def record_run(self, now: datetime):
        self.last_run = now
        self.next = self.__iter.get_next(start_time=now)

    def __str__(self) -> str:
        return f"scheduled.{self.job_config}"
