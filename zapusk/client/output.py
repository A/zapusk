import json
import sys
from pygments import highlight, lexers, formatters

from .printer import Printer


class Output:
    """
    Manages output to a terminal
    """

    def __init__(self, printer=Printer()) -> None:
        self.printer = printer

    def json(self, json_data, colors=False, one_line=False, **kwargs):
        """
        Prints colored JSON into stdout or stderr
        """
        if one_line:
            self.printer.print(json.dumps(json_data), **kwargs)
            return

        formatted_json = json.dumps(json_data, indent=2)

        if not colors:
            self.printer.print(formatted_json, **kwargs)
            return

        colorful_json = highlight(
            formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
        )
        self.printer.print(colorful_json, **kwargs)

    def error(self, exception, **kwargs):
        """
        Prints JSON to stderr
        """
        error = {"error": {"message": exception.message}}
        self.json(error, file=sys.stderr, **kwargs)

    def text(self, *args, **kwargs):
        """
        Prints text
        """
        self.printer.print(*args, **kwargs)
