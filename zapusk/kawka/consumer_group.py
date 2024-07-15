from typing import TypeVar, Generic

from .consumer import Consumer
from .producer import Producer


class ConsumerGroupIterator:
    def __init__(self, producer, from_head):
        self.from_head = from_head
        self.producer = producer
        self.iterator = iter(self.producer.all() if self.from_head else self.producer)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iterator)

    def __str__(self) -> str:
        return f"cg_iter.{self.producer.name}"


C = TypeVar("C", bound=Consumer)


class ConsumerGroup(Generic[C]):
    _consumers: list[C]

    def __init__(
        self,
        producer: Producer,
        Consumer: type[C],
        parallel=1,
        from_head=False,
        name=None,
        context=None,
    ):
        self.context = context
        self.producer = producer
        self.Consumer = Consumer
        self.consumerGroupIterator = ConsumerGroupIterator(
            from_head=from_head, producer=self.producer
        )
        self.parallel = parallel
        self._consumers = []
        self.from_head = from_head

        self.name = name
        if not self.name:
            self.name = type(self).__name__

        self._consumers = [
            Consumer(
                producer=self.consumerGroupIterator,  # type: ignore
                name=f"{self.name}_{i}",
                context=self.context,
            )
            for i in range(self.parallel)
        ]

    def start(self):
        [c.start() for c in self._consumers]

    def join(self, timeout: int):
        [c.join(timeout) for c in self._consumers]
