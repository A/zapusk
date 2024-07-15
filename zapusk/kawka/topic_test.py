from unittest import TestCase

from .topic_iterator import End
from .topic import Topic


class TestTopic(TestCase):
    def test_topic_len_0(self):
        topic = Topic(name="test")

        self.assertEqual(len(topic), 0)

    def test_topic_len_3(self):
        topic = Topic(name="test")
        topic.add(1)
        topic.add(2)
        topic.add(3)

        self.assertEqual(len(topic), 3)

    def test_topic_str(self):
        topic = Topic(name="test")

        self.assertEqual("topic.test", f"{topic}")

    def test_topic_iter_non_block(self):
        topic = Topic(name="test")
        [topic.add(i) for i in range(10)]

        self.assertEqual(
            list(range(10)),
            list(topic.iter(head=topic.head, block=False)),
        )

    def test_topic_iter_block(self):
        topic = Topic(name="test")
        [topic.add(i) for i in range(10)]
        topic.add(End)

        self.assertEqual(
            list(range(10)),
            list(topic.iter(head=topic.head)),
        )
