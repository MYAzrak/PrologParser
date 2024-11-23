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

    def clause(
        self,
    ):  # was getting an error here, I think my white-space logic is wrong?
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
        """<atom> -> <small-atom> | ' <string> '"""
        char = self.lex.getChar()
        if char == "'":
            # Handle quoted string
            self.lex.nextChar()  # consume opening quote
            if not self.string():
                return False
            if self.lex.getChar() != "'":
                self.err.syntax_error("Expected closing quote for string.")
                return False
            self.lex.nextChar()  # consume closing quote
            return True
        else:
            # Handle small-atom
            return self.small_atom()

    def small_atom(self):
        """<small-atom> -> <lowercase-char> | <lowercase-char> <character-list>"""
        if not self.lowercase_char():
            return False

        # Optional character list
        while self.character_list():
            continue
        return True

    def string(self):
        """<string> -> <character> | <character> <string>"""
        if not self.character():
            return False

        # Continue reading characters until we hit a quote or EOF
        char = self.lex.getChar()
        while char and char != "'":
            if not self.character():
                return False
            char = self.lex.getChar()
        return True

    def term_list(self):
        """<term-list> -> <term> | <term> , <term-list>"""
        if not self.term():
            return False

        char = self.lex.getChar()
        while char == ",":
            self.lex.nextChar()  # consume comma
            if not self.term():
                self.err.syntax_error("Expected term after ','.")
                return False
            char = self.lex.getChar()
        return True

    def term(self):
        """<term> -> <atom> | <variable> | <structure> | <numeral>"""
        char = self.lex.getChar()

        if char.isupper() or char == "_":
            # Handle variable
            return self.variable()
        elif char.isdigit():
            # Handle numeral
            return self.numeral()
        else:
            # Try atom first
            pos = self.lex.getPosition()
            if self.atom():
                next_char = self.lex.getChar()
                if next_char == "(":
                    # This is actually a structure
                    self.lex.setPosition(pos)
                    return self.structure()
                return True
            return False

    def structure(self):
        """<structure> -> <atom> ( <term-list> )"""
        if not self.atom():
            return False

        char = self.lex.getChar()
        if char != "(":
            self.err.syntax_error("Expected '(' in structure.")
            return False

        self.lex.nextChar()  # consume '('
        if not self.term_list():
            return False

        if self.lex.getChar() != ")":
            self.err.syntax_error("Expected ')' in structure.")
            return False

        self.lex.nextChar()  # consume ')'
        return True

    def variable(self):
        """<variable> -> <uppercase-char> | <uppercase-char> <character-list>"""
        if not self.uppercase_char():
            return False

        # Optional character list
        while self.character_list():
            continue
        return True

    def lowercase_char(self):
        """<lowercase-char> -> a | b | c | ... | x | y | z"""
        char = self.lex.getChar()
        if char.islower():
            self.lex.nextChar()
            return True
        self.err.syntax_error(f"Expected lowercase character, got '{char}'.")
        return False

    def uppercase_char(self):
        """<uppercase-char> -> A | B | C | ... | X | Y | Z | _"""
        char = self.lex.getChar()
        if char.isupper() or char == "_":
            self.lex.nextChar()
            return True
        self.err.syntax_error(
            f"Expected uppercase character or underscore, got '{char}'."
        )
        return False
