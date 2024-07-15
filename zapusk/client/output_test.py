import sys
from unittest import TestCase
from unittest.mock import patch


from .output import Output
from .printer import Printer


class MockPrinter(Printer):
    def print(self, *args, **kwargs):
        pass


class TestOutput(TestCase):
    def setUp(self) -> None:
        self.mock_printer = MockPrinter()
        return super().setUp()

    def test_should_print_to_stdout(self):
        with patch.object(self.mock_printer, "print") as mock:
            output = Output(printer=self.mock_printer)
            output.text("Hello World!")

            mock.assert_called_with("Hello World!")

    def test_should_print_to_stderr(self):
        with patch.object(self.mock_printer, "print") as mock:
            output = Output(printer=self.mock_printer)
            output.text("Hello World!", file=sys.stderr)

            mock.assert_called_with("Hello World!", file=sys.stderr)

    def test_should_print_json(self):
        with patch.object(self.mock_printer, "print") as mock:
            output = Output(printer=self.mock_printer)
            output.json({"key": "val"})

            mock.assert_called_with('{\n  "key": "val"\n}')

    def test_should_print_json_one_line(self):
        with patch.object(self.mock_printer, "print") as mock:
            output = Output(printer=self.mock_printer)
            output.json({"key": "val"}, one_line=True)

            mock.assert_called_with('{"key": "val"}')

    def test_should_print_json_with_colors(self):
        with patch.object(self.mock_printer, "print") as mock:
            output = Output(printer=self.mock_printer)
            output.json({"key": "val"}, colors=True)

            mock.assert_called_with(
                '{\x1b[37m\x1b[39;49;00m\n\x1b[37m  \x1b[39;49;00m\x1b[94m"key"\x1b[39;49;00m:\x1b[37m \x1b[39;49;00m\x1b[33m"val"\x1b[39;49;00m\x1b[37m\x1b[39;49;00m\n}\x1b[37m\x1b[39;49;00m\n'
            )

    def test_should_print_json_error(self):
        with patch.object(self.mock_printer, "print") as mock:
            output = Output(printer=self.mock_printer)
            output.json({"key": "val"}, file=sys.stderr)

            mock.assert_called_with('{\n  "key": "val"\n}', file=sys.stderr)

    def test_should_print_error(self):
        with patch.object(self.mock_printer, "print") as mock:
            output = Output(printer=self.mock_printer)

            class MockException:
                message = "Hello World!"

            output.error(MockException())

            mock.assert_called_with(
                '{\n  "error": {\n    "message": "Hello World!"\n  }\n}',
                file=sys.stderr,
            )
