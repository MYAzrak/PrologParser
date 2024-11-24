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
        """<program> -> <clause-list> <query> | <query>"""
        # Try clause-list first
        save_position = self.lex.getPosition()
        if self.clause_list():
            if self.query():
                return True
        # If that fails, restore position and try just query
        self.lex.setPosition(*save_position)
        return self.query()

    def clause_list(self):
        """<clause-list> -> <clause> | <clause> <clause-list>"""
        if not self.clause():
            return False
        
        # Look ahead to see if there's another clause
        save_position = self.lex.getPosition()
        if self.clause():
            return self.clause_list()
        self.lex.setPosition(*save_position)
        return True

    def clause(self):
        """<clause> -> <predicate> . | <predicate> :- <predicate-list> ."""
        if not self.predicate():
            return False

        char = self.lex.getChar()
        if char == ".":
            self.lex.nextChar()
            return True
        elif char == ":" and self.lex.nextChar() == "-":
            self.lex.nextChar()  # consume '-'
            if not self.predicate_list():
                self.err.syntax_error("Expected predicate list after ':-'")
                return False
            if self.lex.getChar() != ".":
                self.err.syntax_error("Expected '.' at end of clause")
                return False
            self.lex.nextChar()  # consume '.'
            return True
        self.err.syntax_error("Expected '.' or ':-'")
        return False

    def query(self):
        """<query> -> ?- <predicate-list> ."""
        char = self.lex.getChar()
        if char != "?":
            return False
        if self.lex.nextChar() != "-":
            return False
        self.lex.nextChar()  # consume '-'

        if not self.predicate_list():
            return False

        if self.lex.getChar() != ".":
            self.err.syntax_error("Expected '.' at end of query")
            return False
        self.lex.nextChar()
        return True

    def predicate_list(self):
        """<predicate-list> -> <predicate> | <predicate> , <predicate-list>"""
        if not self.predicate():
            return False

        char = self.lex.getChar()
        if char == ",":
            self.lex.nextChar()
            return self.predicate_list()
        return True

    def predicate(self):
        """<predicate> -> <atom> | <atom> ( <term-list> )"""
        if not self.atom():
            return False

        char = self.lex.getChar()
        if char == "(":
            self.lex.nextChar()
            if not self.term_list():
                self.err.syntax_error("Expected term list after '('")
                return False
            if self.lex.getChar() != ")":
                self.err.syntax_error("Expected ')'")
                return False
            self.lex.nextChar()
        return True

    def term_list(self):
        """<term-list> -> <term> | <term> , <term-list>"""
        if not self.term():
            return False

        char = self.lex.getChar()
        if char == ",":
            self.lex.nextChar()
            return self.term_list()
        return True

    def term(self):
        """<term> -> <atom> | <variable> | <structure> | <numeral>"""
        save_position = self.lex.getPosition()
        
        # Try atom first (which might be part of a structure)
        if self.atom():
            if self.lex.getChar() == "(":  # This is actually a structure
                self.lex.setPosition(*save_position)
                return self.structure()
            return True
            
        # Reset and try variable
        self.lex.setPosition(*save_position)
        if self.variable():
            return True
            
        # Reset and try numeral
        self.lex.setPosition(*save_position)
        return self.numeral()

    def structure(self):
        """<structure> -> <atom> ( <term-list> )"""
        if not self.atom():
            return False

        if self.lex.getChar() != "(":
            return False
        self.lex.nextChar()

        if not self.term_list():
            return False

        if self.lex.getChar() != ")":
            self.err.syntax_error("Expected ')'")
            return False
        self.lex.nextChar()
        return True

    def atom(self):
        """<atom> -> <small-atom> | ' <string> '"""
        char = self.lex.getChar()
        if char == "'":
            self.lex.nextChar()
            if not self.string():
                return False
            if self.lex.getChar() != "'":
                self.err.syntax_error("Expected closing quote")
                return False
            self.lex.nextChar()
            return True
        return self.small_atom()

    def small_atom(self):
        """<small-atom> -> <lowercase-char> <character-list>"""
        if not self.lowercase_char():
            return False
        self.character_list()  # character_list can be empty
        return True

    def string(self):
        """<string> -> <character> | <character> <string>"""
        if not self.character():
            return False
        # Recursively try to match more characters
        next_char = self.lex.getChar()
        if next_char and next_char != "'":
            return self.string()
        return True

    def character(self):
        """<character> -> <alphanumeric> | <special>"""
        save_position = self.lex.getPosition()
        if self.alphanumeric():
            return True
        self.lex.setPosition(*save_position)
        return self.special()

    def special(self):
        """<special> -> + | - | * | / | \\ | ^ | ~ | : | . | ? | # | $ | &"""
        char = self.lex.getChar()
        if char in "+-*/\\^~:.?#$& ":
            self.lex.nextChar()
            return True
        return False

    def character_list(self):
        """<character-list> -> <alphanumeric> <character-list> | ε"""
        save_position = self.lex.getPosition()
        if self.alphanumeric():
            return self.character_list()
        self.lex.setPosition(*save_position)
        return True

    def variable(self):
        """<variable> -> <uppercase-char> <character-list>"""
        if not self.uppercase_char():
            return False
        self.character_list()  # character_list can be empty
        return True

    def alphanumeric(self):
        """<alphanumeric> -> <lowercase-char> | <uppercase-char> | <digit>"""
        save_position = self.lex.getPosition()
        
        if self.lowercase_char():
            return True
            
        self.lex.setPosition(*save_position)
        if self.uppercase_char():
            return True
            
        self.lex.setPosition(*save_position)
        return self.digit()

    def numeral(self):
        """<numeral> -> <digit> | <digit> <numeral>"""
        if not self.digit():
            return False
        # Look ahead for more digits
        save_position = self.lex.getPosition()
        if self.numeral():
            return True
        self.lex.setPosition(*save_position)
        return True

    def digit(self):
        """<digit> -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9"""
        char = self.lex.getChar()
        if char.isdigit():
            self.lex.nextChar()
            return True
        return False

    def lowercase_char(self):
        """<lowercase-char> -> a | b | c | ... | z"""
        char = self.lex.getChar()
        if char.islower():
            self.lex.nextChar()
            return True
        return False

    def uppercase_char(self):
        """<uppercase-char> -> A | B | C | ... | Z | _"""
        char = self.lex.getChar()
        if char.isupper() or char == "_":
            self.lex.nextChar()
            return True
        return False
