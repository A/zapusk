from dataclasses import dataclass
from typing import Optional

from .base_model import BaseModel


@dataclass(eq=False)
class JobConfig(BaseModel):
    id: str
    """
    Job config id
    """

    name: str
    """
    Job name
    """

    command: str
    """
    shell command for the job
    """

    group: str = "default"
    """
    Group id to run job in
    """

    args_command: Optional[str] = None
    """
    callback to fetch arguments to run the command with
    """

    on_finish: Optional[str] = None
    """
    On finish callback
    """

    on_fail: Optional[str] = None
    """
    On fail callback
    """

    schedule: Optional[str] = None
    """
    Cron-like string to define scheduling interval
    """

    def __str__(self) -> str:
        return f"job_config.{self.id}"
