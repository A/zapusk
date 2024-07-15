import logging

logger = logging.getLogger(__name__)


class End:
    pass


class Start:
    pass


class TopicIterator:
    def __init__(self, topic, head, block=True):
        self.topic = topic
        self.block = block

        self.prev = None
        self.cur = head

    def __iter__(self):
        logger.debug(f"{self}: initialized")
        return self

    def __next__(self):
        # Skip Start node
        if self.cur and self.cur.data == Start:
            [self.prev, self.cur] = [self.cur, self.cur.next]

        if self.block:
            # If iterator reached the end of a topic, let's terminate
            if self.cur and self.cur.data is End:
                logger.debug(f"{self}: iterator is over. StopIteration")
                with self.topic.received:
                    self.topic.received.notify()
                raise StopIteration

            if self.prev and not self.cur:
                if not self.prev.next:
                    logger.debug(
                        f"{self}: waiting for upcoming message. self.prev:{self.prev.data}"
                    )
                    with self.topic.received:
                        self.topic.received.wait()

                self.cur = self.prev.next

            # if self.cur is @End, terminate iterator and notify all other readers
            if self.cur and self.cur.data is End:
                logger.debug(f"{self}: StopIteration")
                with self.topic.received:
                    self.topic.received.notify()
                raise StopIteration

            [self.prev, self.cur] = [self.cur, self.cur.next]
            logger.debug(f"{self}: returns {self.prev.data}")
            return self.prev.data

        # Non-block iteration
        if not self.cur or self.cur.data is End:
            logger.debug(f"{self}: StopIteration")
            raise StopIteration

        [self.prev, self.cur] = [self.cur, self.cur.next]
        return self.prev.data

    def __str__(self) -> str:
        return f"iter.{self.topic.name}"
