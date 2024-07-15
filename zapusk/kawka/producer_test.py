from unittest import TestCase
from .producer import Producer


class ProducerTest(TestCase):
    def test_collect_messages_non_block(self):
        producer = Producer(name="test_producer", block=False)
        [producer.add(i) for i in range(10)]
        self.assertEqual(len(producer), 10)
        self.assertEqual(list(producer.all()), list(range(10)))

    def test_block_producer_should_terminate_end(self):
        producer = Producer(name="test_producer", block=True)
        [producer.add(i) for i in [*range(10), Producer.End]]

        # should be ignored
        [producer.add(i) for i in range(10)]
        results = [producer for i in producer.all()]
        self.assertEqual(len(producer), 10)

    def test_producer_should_become_terminated_after_receiving_end(self):
        producer = Producer(name="test_producer", block=True)
        [producer.add(i) for i in [*range(10), Producer.End]]

        l = len(producer)
        [producer.add(i) for i in range(10)]

        self.assertEqual(producer.terminated, True)
        self.assertEqual(len(producer), l)
