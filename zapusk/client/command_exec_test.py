import json
import os
from unittest.mock import call, patch
import responses
from responses import matchers

from .command_testcase import CommandTestCase


class TestCommandExec(CommandTestCase):

    @responses.activate
    def test_should_exec_job(self):
        responses.post(
            "http://example.com/jobs/",
            status=200,
            json={"data": {"id": 1}},
            match=[
                matchers.json_params_matcher(
                    {
                        "command": "echo 1",
                        "group_id": "echo",
                        "name": "Echo",
                        "cwd": "/home/anton/",
                    }
                )
            ],
        )

        self.command_manager.exec.run(
            command="echo 1",
            group_id="echo",
            name="Echo",
            cwd="/home/anton/",
        )
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, {"id": 1})

    @responses.activate
    def test_should_exec_scheduled_job(self):
        responses.post(
            "http://example.com/scheduled-jobs/",
            status=200,
            json={"data": {"id": 1}},
            match=[
                matchers.json_params_matcher(
                    {
                        "command": "echo 1",
                        "group_id": "echo",
                        "name": "Echo",
                        "cwd": "/home/anton/",
                        "schedule": "*/1 * * * *",
                    }
                )
            ],
        )

        self.command_manager.exec.run(
            command="echo 1",
            group_id="echo",
            name="Echo",
            schedule="*/1 * * * *",
            cwd="/home/anton/",
        )
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, {"id": 1})

    @responses.activate
    def test_should_handle_error(self):
        responses.post(
            "http://example.com/jobs/",
            status=400,
            json={"error": "ERROR"},
        )

        self.command_manager.exec.run(
            command="echo 1",
            cwd="/home/anton/",
        )
        args = self.printer.print.call_args[0]
        message = json.loads(args[0])

        self.assertEqual(message, {"error": {"message": "ERROR"}})

    @responses.activate
    def test_should_tail_job(self):
        responses.post(
            "http://example.com/jobs/",
            status=200,
            json={"data": {"id": 1}},
        )
        responses.get(
            "http://example.com/jobs/1",
            status=200,
            json={
                "data": {
                    "id": 1,
                    "log": "/var/tail.log",
                    "cwd": "/home/anton/",
                },
            },
        )

        with patch(
            "zapusk.client.command_tail.tail", return_value=["log line 1", "log line 2"]
        ):
            self.command_manager.exec.run(
                command="echo 1",
                tail=True,
                cwd="/home/anton/",
            )

            log_line1 = self.printer.print.call_args_list[0]
            log_line2 = self.printer.print.call_args_list[1]

            self.assertEqual(log_line1, call("log line 1", end=""))
            self.assertEqual(log_line2, call("log line 2", end=""))
