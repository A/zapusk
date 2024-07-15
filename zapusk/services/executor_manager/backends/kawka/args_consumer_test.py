from unittest import TestCase

from zapusk.kawka import Producer
from zapusk.lib.create_jobitem import create_jobitem
from zapusk.models import Job

from .args_consumer import ArgsConsumer


class ArgsConsumerTest(TestCase):

    def test_should_run_args_command_and_add_arguments_to_a_jobitem(self):
        input_producer = Producer("input_producer")
        sink_producer = Producer("sink_producer")

        args_consumer = ArgsConsumer(
            name="args_consumer",
            producer=input_producer,
            context={
                "sink": sink_producer,
            },
        )

        args_consumer.start()

        item = create_jobitem(command="echo", args_command="echo 1")
        input_producer.add(item)
        input_producer.add(Producer.End)

        args_consumer.join()

        self.assertEqual(item.args, ["1"])
        self.assertEqual(item.state, Job.JOB_STATE_ENUM.PENDING)
        self.assertEqual(len(list(sink_producer.all(block=False))), 1)

    def test_should_pass_items_without_args_command_to_the_sink(self):
        input_producer = Producer("input_producer")
        sink_producer = Producer("sink_producer")

        args_consumer = ArgsConsumer(
            name="args_consumer",
            producer=input_producer,
            context={
                "sink": sink_producer,
            },
        )

        args_consumer.start()

        item = create_jobitem(command="echo")
        input_producer.add(item)
        input_producer.add(Producer.End)

        args_consumer.join()

        self.assertEqual(item.args, [])
        self.assertEqual(item.state, Job.JOB_STATE_ENUM.PENDING)
        self.assertEqual(len(list(sink_producer.all(block=False))), 1)

    def test_should_set_state_to_failed_args_command_fails(self):
        input_producer = Producer("input_producer")
        sink_producer = Producer("sink_producer")

        args_consumer = ArgsConsumer(
            name="args_consumer",
            producer=input_producer,
            context={
                "sink": sink_producer,
            },
        )

        args_consumer.start()

        item = create_jobitem(command="echo", args_command="exit 1")
        input_producer.add(item)
        input_producer.add(Producer.End)

        args_consumer.join()

        self.assertEqual(item.args, [])
        self.assertEqual(item.state, Job.JOB_STATE_ENUM.FAILED)
        self.assertEqual(len(list(sink_producer.all(block=False))), 0)
