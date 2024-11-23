from Lexical import LexicalAnalyzer
from Errors import ErrorHandler


class SyntaxAnalyzer:
    def __init__(self, lexical: LexicalAnalyzer, error: ErrorHandler):
        self.lex = lexical
        self.err = error
        return

    def parse(self):
        return self.program()

    def program(self):
        char = self.lex.getChar()
        if char == "?":
            return self.query()
        return self.clause_list() and self.query()

    def clause_list(self):
        if not self.clause():
            return False

        char = self.lex.getChar()
        while char.isalpha():
            if not self.clause():
                return False
            char = self.lex.getChar()
        return True

    def clause(self):   # was getting an error here, I think my white-space logic is wrong?
        if not self.predicate():
            self.err.syntax_error("Expected a predicate in clause.")
            return False

        char = self.lex.getChar()
        if char == ".":
            self.lex.nextChar()
            return True
        elif char == ":" and self.lex.nextChar() == "-":
            self.lex.nextChar()
            if not self.predicate_list():
                self.err.syntax_error("Expected predicate list after ':-'.")
                return False
            if self.lex.getChar() == ".":
                self.lex.nextChar()
                return True
            self.err.syntax_error("Expected '.' at the end of clause.")
        else:
            self.err.syntax_error("Expected '.' or ':-' in clause.")
        return False

    def query(self):
        char = self.lex.getChar()
        if char != "?":
            self.err.syntax_error("Expected '?-' to start the query.")
            return False
        if self.lex.nextChar() != "-":
            self.err.syntax_error("Expected '-'.")
            return False
        self.lex.nextChar()

        if not self.predicate_list():
            self.err.syntax_error("Expected predicate list in query.")
            return False

        if self.lex.getChar() != ".":
            self.err.syntax_error("Expected '.' at the end of query.")
            return False
        self.lex.nextChar()
        return True

    def special(self):
        return self.lex.getChar() in "+-*/\\^~:.? #$&"

    def character(self):
        return self.alphanumeric() or self.special()

    def alphanumeric(self):
        isAlpha = self.lowercase_char() or self.uppercase_char() or self.digit()
        if not isAlpha:
            self.err.syntax_error(
                f"Expected alphanumeric, got " f"{self.lex.getChar()}"
            )

    def lowercase_char(self):
        return

    def uppercase_char(self):
        return

    def predicate_list(self):
        if not self.predicate():
            return False

        char = self.lex.getChar()
        while char == ",":
            self.lex.nextChar()
            if not self.predicate():
                self.err.syntax_error("Expected predicate after ','.")
                return False
            char = self.lex.getChar()
        return True

    def predicate(self):
        if not self.atom():
            self.err.syntax_error("Expected atom at the start of predicate.")
            return False

        # Check for the '(' indicating the start of a term-list
        char = self.lex.getChar()
        if char == "(":
            self.lex.nextChar()
            if not self.term_list():
                self.err.syntax_error("Expected term list inside '()'.")
                return False
            if self.lex.getChar() != ")":
                self.err.syntax_error("Expected ')' after term list.")
                return False
            self.lex.nextChar()
        return True

    def numeral(self):
        if not self.digit():
            return False

        char = self.lex.getChar()
        while char.isdigit():
            if not self.digit():
                return False
            char = self.lex.getChar()
        return True

    def digit(self):
        char = self.lex.getChar()
        if char.isdigit():
            self.lex.nextChar()  # need to check w/ yousif, what he said about nextChar()
            return True
        self.err.syntax_error(f"Expected digit, got '{char}'.")
        return False

    def atom(self):
        pass

    def term_list(self):   # this needs term as well, need to implement that
        pass
