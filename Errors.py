class ErrorHandler:
    def __init__(self):
        self.errors = []
        return

    def syntax_error(self, error):
        self.errors.append(f"Syntax Error: {error}")

    def report_errors(self):
        if not self.errors:
            print("No errors found.")
        else:
            print("Errors:")
            for error in self.errors:
                print(error)

    def has_errors(self):
        return len(self.errors) > 0
