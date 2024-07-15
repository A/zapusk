from time import sleep
from unittest import TestCase

from zapusk.lib.create_jobitem import create_jobitem
from zapusk.models import Job

from .backend import ExecutorManagerKawkaBackend


class TestKawkaBackend(TestCase):
    def test_kawka_backend_add(self):
        backend = ExecutorManagerKawkaBackend()
        backend.start()

        item = create_jobitem(command="echo 1")
        backend.add(item)
        backend.terminate()

        self.assertEqual(item.state, Job.JOB_STATE_ENUM.FINISHED)

    def test_kawka_backend_get(self):
        backend = ExecutorManagerKawkaBackend()
        backend.start()

        item = create_jobitem(command="echo 1")
        backend.add(item)

        backend.terminate()

        res = backend.get(item.id)

        self.assertEqual(res, item)

    def test_kawka_backend_get_none(self):
        backend = ExecutorManagerKawkaBackend()
        backend.start()

        item = create_jobitem(command="echo 1")
        backend.add(item)

        backend.terminate()

        res = backend.get(999)

        self.assertEqual(res, None)

    def test_kawka_backend_list(self):
        backend = ExecutorManagerKawkaBackend()
        backend.start()

        backend.add(create_jobitem(command="echo 1"))
        backend.add(create_jobitem(command="echo 2"))
        backend.add(create_jobitem(command="echo 3"))

        backend.terminate()

        res = backend.list()

        self.assertEqual(len(res), 3)
        self.assertEqual(res[0].command, "echo 1")
        self.assertEqual(res[1].command, "echo 2")
        self.assertEqual(res[2].command, "echo 3")

    def test_kawka_backend_cancel(self):
        backend = ExecutorManagerKawkaBackend()
        backend.start()

        item = create_jobitem(command="sleep 10")
        backend.add(item)

        sleep(1)

        res = backend.get(item.id)

        if not res:
            raise Exception("Fail")

        self.assertEqual(res.state, Job.JOB_STATE_ENUM.RUNNING)

        backend.cancel(item)
        sleep(1)

        self.assertEqual(item.state, Job.JOB_STATE_ENUM.CANCELLED)

        backend.terminate()
