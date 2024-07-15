import logging
from .topic import Topic, End

logger = logging.getLogger(__name__)


class Producer:
    End = End

    terminated = False

    def __init__(self, name, block=True):
        self.name = name

        self.__topic = Topic(name=self.name)
        self.__block = block
        logger.info(f"{self}: initialized")

    def add(self, msg):
        # TODO: probably, not needed
        logger.info(f"{self}: collected a message {msg}")

        if self.terminated:
            return

        if msg == End:
            self.terminated = True
            logger.info(f"{self}: terminated")

        self.__topic.add(msg)

    def all(self, block=None):
        """
        Iterate over all items from head
        """
        if block is not None:
            return self.__topic.iter(block=block, head=self.__topic.head)

        return self.__topic.iter(block=self.__block, head=self.__topic.head)

    def __len__(self):
        return len(self.__topic)

    def __iter__(self):
        """
        Iterate from current message
        """
        return self.__topic.iter(block=self.__block, head=self.__topic.last)

    def __str__(self) -> str:
        return f"producer.{self.name}"
