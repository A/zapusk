class Printer:
    """
    Was created to mock in the tests, because by some reasons I can't
    manage neither testfixtures nor pytest to capture output properly
    """

    def print(self, *args, **kwargs):
        """
        Prints given data via `print` to terminal
        """
        print(*args, **kwargs)
