from dataclasses import dataclass, field
from .base_model import BaseModel

from .job_config import JobConfig
from .job_group import JobGroup


@dataclass(eq=False)
class Config(BaseModel):
    port: int
    colors: bool
    job_groups: dict[str, JobGroup] = field(default_factory=dict)
    jobs: dict[str, JobConfig] = field(default_factory=dict)
