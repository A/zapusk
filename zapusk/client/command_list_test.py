import json
import responses

from zapusk.models.job import JOB_STATE_ENUM

from .command_testcase import CommandTestCase


class TestCommandList(CommandTestCase):
    @responses.activate
    def test_should_list_jobs(self):
        data = [
            {
                "id": 1,
                "state": JOB_STATE_ENUM.PENDING,
            },
            {
                "id": 2,
                "state": JOB_STATE_ENUM.RUNNING,
            },
        ]

        responses.get("http://example.com/jobs/", status=200, json={"data": data})

        self.command_manager.list.run()
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, data)

    @responses.activate
    def test_should_list_jobs_with_filter(self):
        data = [
            {
                "id": 1,
                "state": JOB_STATE_ENUM.PENDING,
            },
            {
                "id": 2,
                "state": JOB_STATE_ENUM.RUNNING,
            },
        ]

        responses.get("http://example.com/jobs/", status=200, json={"data": data})

        self.command_manager.list.run(filter=JOB_STATE_ENUM.PENDING)
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, [data[0]])

    @responses.activate
    def test_should_list_scheduled_jobs(self):
        data = [
            {
                "id": 1,
            },
        ]

        responses.get(
            "http://example.com/scheduled-jobs/", status=200, json={"data": data}
        )

        self.command_manager.list.run(scheduled=True)
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, data)

    @responses.activate
    def test_should_list_jobs_error(self):
        responses.get("http://example.com/jobs/", status=400, json={"error": "ERROR"})

        self.command_manager.list.run()
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, {"error": {"message": "ERROR"}})
