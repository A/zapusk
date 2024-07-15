import threading

from .linked_list import LinkedList
from .topic_iterator import TopicIterator, Start, End


type L[T] = T | type[Start] | type[End]


class Topic[T]:
    """
    Topic is a linked list data structure designed to add, store and iterate over its messages.
    """

    head: LinkedList[L[T]]
    """
    Link to the first element of the topic
    """

    last: LinkedList[L[T]]
    """
    Link to the last element of the topic
    """

    def __init__(self, name: str):
        self.name = name
        self.mutex = threading.Lock()
        self.received = threading.Condition(self.mutex)

        self.head = LinkedList(Start)
        self.last = self.head

    def __len__(self):
        iter = TopicIterator(block=False, topic=self, head=self.head)
        return len(list(iter))

    def add(self, data: T):
        """
        Append a new item to a topic
        """
        with self.mutex:
            self.last = self.last.append(data)
            self.received.notify()
        return self

    def iter(self, block=True, head=None):
        """
        Creates a blocking or non-blocking iterator over a topic.
        """
        return TopicIterator(block=block, topic=self, head=head)

    def __str__(self) -> str:
        return f"topic.{self.name}"
