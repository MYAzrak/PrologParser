from Lexical import LexicalAnalyser
from Errors import ErrorHandler


class SyntaxAnalyser:
    def __init__(self, lexical: LexicalAnalyser, error: ErrorHandler):
        self.lex = lexical
        self.err = error
        return

    def parse(self):
        return self.program()

    def program(self):
        return

    def clause_list(self):
        return

    def special(self):
        return self.lex.getChar() in '+-*/\\^~:.? #$&'

    def character(self):
        return self.alphanumeric() or self.special()

    def alphanumeric(self):
        isAlpha = self.lowercase_char() or self.uppercase_char() or self.digit()
        if not isAlpha:
            self.err.syntax_error(f"Expected alphanumeric, got "
                                  f"{self.lex.getChar()}")

    def lowercase_char(self):
        return

    def uppercase_char(self):
        return

    def digit(self):
        return
