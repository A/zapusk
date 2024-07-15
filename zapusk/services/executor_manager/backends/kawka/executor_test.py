import os
from unittest import TestCase, mock
from testfixtures.mock import call
from testfixtures import Replacer
from testfixtures.popen import MockPopen

from zapusk.kawka import Producer
from zapusk.lib.create_jobitem import create_jobitem
from zapusk.models import Job

from .executor import Executor


class ExecutorTest(TestCase):
    def setUp(self):
        self.Popen = MockPopen()
        self.r = Replacer()
        self.r.replace("subprocess.Popen", self.Popen)
        self.r.in_environ("HOME", "/home/")
        self.addCleanup(self.r.restore)

    def test_consumer_should_run_command(self):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("echo 1", stdout=b"1", stderr=b"")
        item = create_jobitem(command="echo 1")
        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join()

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "echo 1",
                shell=True,
                env={**os.environ},
                cwd="/home/",
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )
        self.assertEqual(item.state, Job.JOB_STATE_ENUM.FINISHED)

    def test_consumer_should_run_on_finish_callback(self):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("echo 1", stdout=b"1", stderr=b"")
        self.Popen.set_command("echo finish", stdout=b"finish", stderr=b"")

        item = create_jobitem(command="echo 1", on_finish="echo finish")

        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join()

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "echo 1",
                shell=True,
                env={**os.environ},
                cwd="/home/",
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )

        self.assertEqual(
            self.Popen.all_calls[2],
            call.Popen(
                "echo finish",
                env={**os.environ},
                cwd="/home/",
                shell=True,
            ),
        )

    def test_consumer_should_run_on_finish_group_callback(self):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("echo 1", stdout=b"1", stderr=b"")
        self.Popen.set_command("echo finish", stdout=b"finish", stderr=b"")

        item = create_jobitem(command="echo 1", group_on_finish="echo finish")

        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join()

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "echo 1",
                env={**os.environ},
                cwd="/home/",
                shell=True,
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )

        self.assertEqual(
            self.Popen.all_calls[2],
            call.Popen(
                "echo finish",
                env={**os.environ},
                cwd="/home/",
                shell=True,
            ),
        )

    def test_consumer_should_run_on_finish_job_callback_if_both_job_and_group_are_defined(
        self,
    ):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("echo 1", stdout=b"1", stderr=b"")
        self.Popen.set_command("echo finish", stdout=b"finish", stderr=b"")

        item = create_jobitem(
            command="echo 1",
            on_finish="echo finish",
            group_on_finish="echo finish_group",
        )

        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join()

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "echo 1",
                shell=True,
                env={**os.environ},
                cwd="/home/",
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )

        self.assertEqual(
            self.Popen.all_calls[2],
            call.Popen(
                "echo finish",
                env={**os.environ},
                cwd="/home/",
                shell=True,
            ),
        )

    def test_consumer_should_run_on_fail_callback(self):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("exit 1", stdout=b"", stderr=b"1", returncode=1)
        self.Popen.set_command("echo fail", stdout=b"fail", stderr=b"")

        item = create_jobitem(command="exit 1", on_fail="echo fail")

        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join()

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "exit 1",
                env={**os.environ},
                cwd="/home/",
                shell=True,
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )

        self.assertEqual(
            self.Popen.all_calls[2],
            call.Popen(
                "echo fail",
                env={**os.environ},
                cwd="/home/",
                shell=True,
            ),
        )

    def test_consumer_should_run_group_on_fail_callback(self):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("exit 1", stdout=b"", stderr=b"1", returncode=1)
        self.Popen.set_command("echo fail", stdout=b"fail", stderr=b"")

        item = create_jobitem(command="exit 1", group_on_fail="echo fail")

        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join()

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "exit 1",
                env={**os.environ},
                cwd="/home/",
                shell=True,
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )

        self.assertEqual(
            self.Popen.all_calls[2],
            call.Popen(
                "echo fail",
                env={**os.environ},
                cwd="/home/",
                shell=True,
            ),
        )

    def test_consumer_should_run_on_fail_job_callback_if_both_job_and_group_callbacks_are_defined(
        self,
    ):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("exit 1", stdout=b"", stderr=b"1", returncode=1)
        self.Popen.set_command("echo fail", stdout=b"fail", stderr=b"")

        item = create_jobitem(
            command="exit 1", on_fail="echo fail", group_on_fail="echo group_fail"
        )

        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join()

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "exit 1",
                env={**os.environ},
                cwd="/home/",
                shell=True,
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )

        self.assertEqual(
            self.Popen.all_calls[2],
            call.Popen(
                "echo fail",
                env={**os.environ},
                cwd="/home/",
                shell=True,
            ),
        )

    def test_consumer_should_run_command_with_args(self):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("echo 1 2 3", stdout=b"1 2 3", stderr=b"")
        item = create_jobitem(command="echo", args=["1", "2", "3"])
        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join(2)

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "echo 1 2 3",
                env={**os.environ},
                cwd="/home/",
                shell=True,
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )
        self.assertEqual(item.state, Job.JOB_STATE_ENUM.FINISHED)

    def test_consumer_should_fail_command(self):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("exit 1", stdout=b"1", stderr=b"", returncode=1)
        item = create_jobitem(command="exit 1")
        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join(2)

        self.assertEqual(
            self.Popen.all_calls[0],
            call.Popen(
                "exit 1",
                env={**os.environ},
                cwd="/home/",
                shell=True,
                stdout=mock.ANY,
                stderr=mock.ANY,
            ),
        )
        self.assertEqual(item.state, Job.JOB_STATE_ENUM.FAILED)

    def test_consumer_should_skip_cancelled(self):
        input_producer = Producer("input_producer")
        executor = Executor(name="run_consumer", producer=input_producer)
        executor.start()

        self.Popen.set_command("exit 1", stdout=b"1", stderr=b"", returncode=1)
        item = create_jobitem(command="exit 1", state=Job.JOB_STATE_ENUM.CANCELLED)
        input_producer.add(item)
        input_producer.add(Producer.End)

        executor.join(2)

        self.assertEqual(len(self.Popen.all_calls), 0)
        self.assertEqual(item.state, Job.JOB_STATE_ENUM.CANCELLED)
