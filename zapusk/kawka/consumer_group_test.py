from time import sleep
import itertools
from unittest import TestCase

from .consumer import Consumer
from .consumer_group import ConsumerGroup
from .producer import Producer


class DummyConsumer(Consumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []

    def process(self, msg):
        sleep(0.01)
        msg["consumed_by"] = self.name
        self.results.append(msg)


class ConsumerGroupTest(TestCase):
    def test_consumergroup_seq100_parallel1(self):
        producer = Producer(name="test_producer", block=True)

        cg = ConsumerGroup(producer=producer, Consumer=DummyConsumer, parallel=1)
        cg.start()

        [producer.add({"id": i, "consumed_by": None}) for i in range(100)]
        producer.add(Producer.End)

        cg.join(5)
        c = cg._consumers[0]

        self.assertEqual(len(c.results), 100)
        self.assertEqual(
            all(map(lambda x: type(x["consumed_by"]) == str, c.results)), True
        )

    def test_consumergroup_seq100_parallel2(self):
        producer = Producer(name="test_producer", block=True)

        cg = ConsumerGroup(
            name="DummyGroup",
            producer=producer,
            Consumer=DummyConsumer,
            parallel=2,
        )
        cg.start()

        [producer.add({"id": i, "consumed_by": None}) for i in range(100)]
        producer.add(Producer.End)

        cg.join(5)

        results = [c.results for c in cg._consumers]
        results = list(itertools.chain.from_iterable(results))

        consumed_by = list(map(lambda x: x["consumed_by"], results))

        self.assertEqual(len(results), 100)

        self.assertEqual(any(map(lambda x: x == "DummyGroup_0", consumed_by)), True)
        self.assertEqual(any(map(lambda x: x == "DummyGroup_1", consumed_by)), True)

    def test_consumergroup_sink(self):
        input_producer = Producer(name="input_producer", block=True)
        sink_producer = Producer(name="sink_producer", block=True)

        class SinkConsumer(Consumer):
            def process(self, msg):
                self.context["sink"].add(msg)  # type: ignore

        cg = ConsumerGroup(
            name="SinkGroup",
            producer=input_producer,
            Consumer=SinkConsumer,
            parallel=1,
            context={
                "sink": sink_producer,
            },
        )
        cg.start()

        [input_producer.add({"id": i}) for i in range(100)]
        input_producer.add(Producer.End)

        cg.join(2)

        self.assertEqual(len(list(sink_producer.all(block=False))), 100)
