import json
from unittest.mock import call, patch
import responses

from .command_testcase import CommandTestCase


class TestCommandExec(CommandTestCase):
    @responses.activate
    def test_should_tail_job(self):
        responses.get(
            "http://example.com/jobs/1",
            status=200,
            json={"data": {"id": 1, "log": None}},
        )

        responses.get(
            "http://example.com/jobs/1",
            status=200,
            json={"data": {"id": 1, "log": "/var/tail.log"}},
        )

        with patch(
            "zapusk.client.command_tail.tail", return_value=["log line 1", "log line 2"]
        ):
            self.command_manager.tail.run(job_id=1)

            log_line1 = self.printer.print.call_args_list[0]
            log_line2 = self.printer.print.call_args_list[1]

            self.assertEqual(log_line1, call("log line 1", end=""))
            self.assertEqual(log_line2, call("log line 2", end=""))

    @responses.activate
    def test_should_handle_error(self):
        responses.get("http://example.com/jobs/1", status=400, json={"error": "ERROR"})

        self.command_manager.tail.run(job_id=1)
        args = self.printer.print.call_args[0]
        message = json.loads(args[0])

        self.assertEqual(message, {"error": {"message": "ERROR"}})
