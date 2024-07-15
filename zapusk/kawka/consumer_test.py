from time import sleep
from unittest import TestCase

from .consumer import Consumer
from .producer import Producer


class DummyConsumer(Consumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []

    def process(self, msg):
        msg["consumed"] = True
        self.results.append(msg)


class SleepyConsumer(Consumer):
    def __init__(self, sleep=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep = sleep
        self.results = []

    def process(self, msg):
        sleep(self.sleep)
        msg["consumed"] = True
        self.results.append(msg)


class ConsumerTest(TestCase):
    def test_read_from_non_block_producer_head(self):
        producer = Producer(name="DummyProducer", block=False)
        consumer = DummyConsumer(producer=producer, from_head=True)

        [producer.add({"id": i, "consumed": False}) for i in range(10)]

        consumer.start()
        consumer.join()

        self.assertEqual(len(consumer.results), 10)
        self.assertEqual(all(map(lambda x: x["consumed"], consumer.results)), True)

    def test_read_from_block_producer_head(self):
        producer = Producer(name="DummyProducer", block=True)
        consumer = DummyConsumer(producer=producer, from_head=True)

        [producer.add({"id": i, "consumed": False}) for i in range(10)]
        producer.add(Producer.End)

        consumer.start()
        consumer.join()

        self.assertEqual(len(consumer.results), 10)
        self.assertEqual(all(map(lambda x: x["consumed"], consumer.results)), True)

    def test_read_from_producer_tail(self):
        producer = Producer(name="DummyProducer", block=True)

        # This events should be ignored, because no consumer yet
        [producer.add({"id": i, "consumed": False}) for i in range(-10, 0)]

        # Now start a consumer. It will take only the last item with id -1
        consumer = DummyConsumer(producer=producer)
        consumer.results = []
        consumer.start()

        # And handle this events
        [producer.add({"id": i, "consumed": False}) for i in range(10)]
        producer.add(Producer.End)

        consumer.join()
        self.assertEqual(len(consumer.results), 11)
        self.assertEqual(all(map(lambda x: x["consumed"], consumer.results)), True)
        self.assertEqual(
            list(map(lambda x: x["id"], consumer.results)), list(range(-1, 10))
        )

    def test_slow_consumer(self):
        producer = Producer(name="DummyProducer", block=True)
        consumer = SleepyConsumer(producer=producer, sleep=1)
        consumer.start()

        producer.add({"id": 1, "consumed": False})
        sleep(0.5)
        producer.add({"id": 2, "consumed": False})
        producer.add(Producer.End)

        consumer.join()

        self.assertEqual(len(consumer.results), 2)
        self.assertEqual(all(map(lambda x: x["consumed"], consumer.results)), True)
