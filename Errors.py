class ErrorHandler:
    def __init__(self):
        self.errors = []
        return

    def syntax_error(self, error):
        return

    def report_errors(self):
        map(print, self.errors)
