import json
import responses

from .command_testcase import CommandTestCase


class TestCommandCancel(CommandTestCase):
    @responses.activate
    def test_should_cancel_job(self):
        responses.delete("http://example.com/jobs/1", status=200, json={"data": True})

        self.command_manager.cancel.run(job_id=1)
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, True)

    @responses.activate
    def test_should_cancel_scheduled_job(self):
        responses.delete(
            "http://example.com/scheduled-jobs/1", status=200, json={"data": True}
        )

        self.command_manager.cancel.run(job_id=1, scheduled=True)
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, True)

    @responses.activate
    def test_should_handle_error(self):
        responses.delete(
            "http://example.com/jobs/1", status=400, json={"error": "ERROR"}
        )

        self.command_manager.cancel.run(job_id=1)
        args = self.printer.print.call_args[0]
        message = json.loads(args[0])

        self.assertEqual(message, {"error": {"message": "ERROR"}})
