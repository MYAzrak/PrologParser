class ErrorHandler:
    def __init__(self, lex):
        self.errors = []
        self.lex = lex
        self.recovery_points = {"."}
        self.error_positions = set()  # Track positions where errors occurred
        return

    def syntax_error(self, error):
        # Only add the error if we haven't seen it at this position before
        current_pos = self.lex.getPosition()
        line, pos = current_pos
        if current_pos not in self.error_positions:
            self.error_positions.add(current_pos)
            line_text = self.lex.getLine()
            pointer = ' ' * pos + '^'  # Create pointer at error position
            
            # Add newline only if the line doesn't already end with one
            line_ending = '' if line_text.endswith('\n') else '\n'
            self.errors.append(f"Syntax Error: {error} at {current_pos}\n{line_text}{line_ending}{pointer}")

    def report_errors(self):
        if not self.errors:
            print("No errors found.")
        else:
            print("Errors:")
            for error in self.errors:
                print()
                print(error)
                print()

    def has_errors(self):
        return len(self.errors) > 0
    
    def recover_to_next_clause(self):
        """
        Skip tokens until we reach a recovery point ('.') and position ourselves
        at the start of the next potential clause.
        Returns True if recovery was successful, False if we reached end of input
        """
        # Keep track of starting position to ensure we make progress
        start_position = self.lex.getPosition()
        found_period = False
        
        while self.lex.getChar():
            if self.lex.getChar() == ".":
                found_period = True
                self.lex.nextChar()  # Consume the period
                break
            self.lex.nextChar()
            
        # If we didn't find a period and didn't move, force advance
        if not found_period and self.lex.getPosition() == start_position:
            self.lex.nextChar()
            
        return bool(self.lex.getChar())
