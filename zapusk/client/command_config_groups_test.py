import json
import responses

from .command_testcase import CommandTestCase


class TestCommandConfigGroups(CommandTestCase):
    @responses.activate
    def test_should_cancel_job(self):
        data = [
            {"id": 1},
            {"id": 2},
        ]

        responses.get(
            "http://example.com/config/groups/", status=200, json={"data": data}
        )

        self.command_manager.config_groups.run()
        json_data = json.loads(self.printer.print.call_args[0][0])

        self.assertEqual(json_data, data)

    @responses.activate
    def test_should_handle_error(self):
        responses.get(
            "http://example.com/config/groups/", status=400, json={"error": "ERROR"}
        )

        self.command_manager.config_groups.run()
        args = self.printer.print.call_args[0]
        message = json.loads(args[0])

        self.assertEqual(message, {"error": {"message": "ERROR"}})
