import json
import responses
from responses import matchers

from .command_testcase import CommandTestCase


class TestCommandRun(CommandTestCase):
    @responses.activate
    def test_should_run_job(self):
        # TODO: check only tail command has been run
        data = [{"id": 1}]

        responses.post(
            "http://example.com/jobs/",
            status=200,
            json={"data": data},
            match=[
                matchers.json_params_matcher(
                    {
                        "job_config_id": "echo",
                    }
                )
            ],
        )

        self.command_manager.run.run(job_config_id="echo")
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, data)

    @responses.activate
    def test_should_handle_error(self):
        responses.post("http://example.com/jobs/", status=400, json={"error": "ERROR"})

        self.command_manager.run.run(job_config_id="echo")
        args = self.printer.print.call_args[0]
        message = json.loads(args[0])

        self.assertEqual(message, {"error": {"message": "ERROR"}})
