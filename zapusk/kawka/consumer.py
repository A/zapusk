import logging
from threading import Thread
from typing import Any, Optional

from .producer import Producer

logger = logging.getLogger(__name__)


class Consumer(Thread):
    def __init__(
        self,
        producer: Producer,
        name: Optional[str] = None,
        from_head=False,
        context: Optional[dict[str, Any]] = None,
        *args,
        **kwargs,
    ):
        super(Consumer, self).__init__(*args, **kwargs)
        self.context: dict[str, Any] = context or {}
        self.producer = producer
        self.from_head = from_head
        self.name = name if name else type(self).__name__

    def on_end(self):
        logger.info(f"{self} reached the very end of the {self.producer}")
        pass

    def process(self, msg, *args, **kwargs):
        logger.info(f"{self}: process {msg}")  # pragma: no cover

    def run(self):
        logger.info(f"{self}: start polling events")
        iterator = self.producer.all() if self.from_head else self.producer

        for msg in iterator:
            logger.info(f"{self}: message received {msg}")
            self.process(msg)
            logger.info(f"{self}: waiting for upcoming message")

        self.on_end()

    def __str__(self) -> str:
        return f"consumer.{self.name}"
