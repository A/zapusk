from unittest import TestCase

import pytest
from .printer import Printer


class TestPrinter(TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_printer_should_print(self):
        printer = Printer()

        printer.print("test")
        out, _ = self.capsys.readouterr()

        self.assertEqual(out, "test\n")
