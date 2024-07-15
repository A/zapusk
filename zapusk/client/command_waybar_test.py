import json
import datetime
import responses

from zapusk.models.job import JOB_STATE_ENUM

from .command_testcase import CommandTestCase


class TestCommandRun(CommandTestCase):
    @responses.activate
    def test_should_run_job(self):
        now = datetime.datetime.now()
        ago_1m = str(now - datetime.timedelta(minutes=1))
        ago_1h = str(now - datetime.timedelta(hours=1))
        ago_1d = str(now - datetime.timedelta(days=1))
        ago_7d = str(now - datetime.timedelta(days=7))

        data = [
            {
                "id": 1,
                "name": "P",
                "state": JOB_STATE_ENUM.PENDING,
                "updated_at": ago_1m,
            },
            {
                "id": 2,
                "name": "R",
                "state": JOB_STATE_ENUM.RUNNING,
                "updated_at": ago_1h,
            },
            {
                "id": 3,
                "name": "C",
                "state": JOB_STATE_ENUM.CANCELLED,
                "updated_at": ago_1d,
            },
            {
                "id": 4,
                "name": "D",
                "state": JOB_STATE_ENUM.FINISHED,
                "updated_at": ago_7d,
            },
            {
                "id": 5,
                "name": "F",
                "state": JOB_STATE_ENUM.FAILED,
                "updated_at": ago_1m,
            },
        ]

        responses.get(
            "http://example.com/jobs/",
            status=200,
            json={"data": data},
            match=[],
        )

        self.command_manager.waybar.run()
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(
            json_data["text"], "\uf4ab  1 \uf144  1 \uf058  1 \uf06a  1 \uf057  1"
        )
        self.assertEqual(
            json_data["tooltip"],
            "\r\n".join(
                [
                    "<b>F(id=5)</b> <i>failed a minute ago</i>",
                    "<b>D(id=4)</b> <i>finished 7 days ago</i>",
                    "<b>C(id=3)</b> <i>cancelled a day ago</i>",
                    "<b>R(id=2)</b> <i>started an hour ago</i>",
                    "<b>P(id=1)</b> <i>queued a minute ago</i>",
                ]
            ),
        )

    @responses.activate
    def test_should_handle_error(self):
        responses.get("http://example.com/jobs/", status=400, json={"error": "ERROR"})

        self.command_manager.waybar.run()
        args = self.printer.print.call_args[0]
        message = json.loads(args[0])

        self.assertEqual(message, {"text": "ERROR"})
