class ErrorHandler:
    def __init__(self, lex):
        self.errors = []
        self.lex = lex
        return

    def syntax_error(self, error):
        self.errors.append(f"Syntax Error: {error} at {self.lex.getPosition()}")

    def report_errors(self):
        if not self.errors:
            print("No errors found.")
        else:
            print("Errors:")
            for error in self.errors:
                print(error)

    def has_errors(self):
        return len(self.errors) > 0
