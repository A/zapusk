from time import sleep
from unittest import TestCase, mock
from testfixtures.mock import call
from testfixtures import Replacer
from testfixtures.popen import MockPopen

from zapusk.kawka import Producer
from zapusk.lib.create_jobitem import create_jobitem
from zapusk.models import Job

from .consumer import ExecutorManagerConsumer


class ExecutorManagerTest(TestCase):
    def setUp(self):
        self.Popen = MockPopen()
        self.r = Replacer()
        self.r.replace("subprocess.Popen", self.Popen)
        self.addCleanup(self.r.restore)

    def test_should_get_args_and_run_job(self):
        input_producer = Producer(name="input_producer")

        executor_manager = ExecutorManagerConsumer(
            name="run_consumer",
            producer=input_producer,
        )
        executor_manager.start()

        self.Popen.set_command("get_args", stdout=b"hello world", stderr=b"")
        self.Popen.set_command(
            "my_command hello world", stdout=b"hello world", stderr=b""
        )

        item = create_jobitem(command="my_command", args_command="get_args")

        input_producer.add(item)
        input_producer.add(Producer.End)

        sleep(1)
        executor_manager.join(2)

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "get_args",
                shell=True,
                stdout=-1,
                stderr=-1,
            ),
        )
        self.assertEqual(
            self.Popen.all_calls[3],
            call.Popen(
                "my_command hello world",
                shell=True,
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )
        self.assertEqual(item.state, Job.JOB_STATE_ENUM.FINISHED)
