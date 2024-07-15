from dataclasses import dataclass
from typing import Optional

from .base_model import BaseModel


@dataclass(eq=False)
class JobGroup(BaseModel):
    id: str
    parallel: int
    on_finish: Optional[str] = None
    on_fail: Optional[str] = None

    def __post_init__(self):
        if self.parallel <= 0:
            raise ValueError("`parallel` must be a positive number")
