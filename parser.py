from enum import Enum, auto


class Token(Enum):
    # Special characters
    DOT = auto()  # .
    COMMA = auto()  # ,
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    QUERY = auto()  # ?-
    IMPLIES = auto()  # :-
    QUOTE = auto()  # '

    # Character types
    LOWERCASE = auto()  # a-z
    UPPERCASE = auto()  # A-Z, _
    DIGIT = auto()  # 0-9
    SPECIAL = auto()  # +, -, *, /, \, ^, ~, :, ., ?, #, $, &
    SPACE = auto()  # space

    # Other
    EOF = auto()  # End of input
    UNKNOWN = auto()

    def __str__(self):
        return self.name


class LexicalAnalyzer:
    def __init__(self, program):
        self.line = 0
        self.position = 0
        self.input_lines = program
        self.current_char = None
        self.current_token = None

    def getChar(self, keep_space=False):
        """Returns the current character without consuming it"""
        try:
            c = self.input_lines[self.line][self.position]
            if not keep_space and c == " ":
                self.nextChar()
                return self.getChar()
            return c
        except IndexError:
            return None

    def getCurrentChar(self):
        """Returns the actual character at current position"""
        return self.getChar(keep_space=True)

    def getToken(self):
        """Returns the token enum for the current character"""
        char = self.getChar()

        if char is None:
            return Token.EOF

        if char.isspace():
            return Token.SPACE

        if char.islower():
            return Token.LOWERCASE

        if char.isupper() or char == "_":
            return Token.UPPERCASE

        if char.isdigit():
            return Token.DIGIT

        # Check multi-character tokens first
        if char == "?" and self.peekNext() == "-":
            return Token.QUERY

        if char == ":" and self.peekNext() == "-":
            return Token.IMPLIES

        # Single character tokens
        token_map = {
            ".": Token.DOT,
            ",": Token.COMMA,
            "(": Token.LPAREN,
            ")": Token.RPAREN,
            "'": Token.QUOTE,
        }

        if char in token_map:
            return token_map[char]

        if char in "+-*/\\^~:.?# $&":
            return Token.SPECIAL

        return Token.UNKNOWN

    def peekNext(self):
        """Look at next character without consuming current one"""
        if self.position + 1 < len(self.input_lines[self.line]):
            return self.input_lines[self.line][self.position + 1]
        return None

    def nextChar(self):
        """Advance to next character and return it"""
        if self.position < len(self.input_lines[self.line]) - 1:
            self.position += 1
        else:
            self.line += 1
            self.position = 0

        if self.line >= len(self.input_lines):
            return None

        char = self.getChar()
        if char == "\n":
            return self.nextChar()

        return char

    def getPosition(self):
        return self.line, self.position

    def setPosition(self, line, position):
        self.line = line
        self.position = position

    def getLine(self):
        return self.input_lines[self.line]


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
            pointer = " " * pos + "^"  # Create pointer at error position

            # Add newline only if the line doesn't already end with one
            line_ending = "" if line_text.endswith("\n") else "\n"
            self.errors.append(
                f"Syntax Error: {error} at {current_pos}\n{line_text}{line_ending}{pointer}"
            )

    def report_errors(self):
        if not self.errors:
            print("No errors found.")
        else:
            print("Errors:")
            for error in self.errors:
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


class SyntaxAnalyzer:
    def __init__(self, lexical: LexicalAnalyzer, error: ErrorHandler):
        self.lex = lexical
        self.err = error

    def parse(self):
        """Parse the entire program with error recovery"""
        success = True
        while self.lex.getToken() != Token.EOF:
            start_position = self.lex.getPosition()

            try:
                if not self.program():
                    success = False
                    if self.lex.getPosition() == start_position:
                        self.err.recover_to_next_clause()
            except Exception as e:
                success = False
                self.err.syntax_error(str(e))
                if self.lex.getPosition() == start_position:
                    self.err.recover_to_next_clause()

            if self.lex.getPosition() == start_position:
                if not self.lex.nextChar():
                    break

        return success

    def program(self):
        """<program> -> <clause-list> <query> | <query>"""
        save_position = self.lex.getPosition()

        # Try clause-list first
        try:
            if self.clause_list():
                if self.query():
                    return True
        except Exception:
            # Don't handle the exception here, let it propagate up
            raise

        # If that fails, restore position and try just query
        self.lex.setPosition(*save_position)
        return self.query()

    def clause(self):
        """<clause> -> <predicate> . | <predicate> :- <predicate-list> ."""
        if not self.predicate():
            return False

        token = self.lex.getToken()
        if token == Token.DOT:
            self.lex.nextChar()
            return True
        elif token == Token.IMPLIES:
            self.lex.nextChar()  # consume ':-'
            self.lex.nextChar()  # consume the second character
            if not self.predicate_list():
                self.err.syntax_error("Expected predicate list after ':-'")
                return False
            if self.lex.getToken() != Token.DOT:
                self.err.syntax_error("Expected '.' at end of clause")
                return False
            self.lex.nextChar()
            return True
        self.err.syntax_error("Expected '.' or ':-'")
        return False

    def query(self):
        """<query> -> ?- <predicate-list> ."""
        if self.lex.getToken() != Token.QUERY:
            return False
        self.lex.nextChar()  # consume '?'
        self.lex.nextChar()  # consume '-'

        if not self.predicate_list():
            return False

        if self.lex.getToken() != Token.DOT:
            self.err.syntax_error("Expected '.' at end of query")
            return False
        self.lex.nextChar()
        return True

    def predicate(self):
        """<predicate> -> <atom> | <atom> ( <term-list> )"""
        if not self.atom():
            return False

        if self.lex.getToken() == Token.LPAREN:
            self.lex.nextChar()
            if not self.term_list():
                self.err.syntax_error("Expected term list after '(' in a predicate")
                return False
            if self.lex.getToken() != Token.RPAREN:
                self.err.syntax_error("Expected ')' after term list")
                return False
            self.lex.nextChar()
        return True

    def lowercase_char(self):
        """<lowercase-char> -> a | b | c | ... | z"""
        if self.lex.getToken() == Token.LOWERCASE:
            self.lex.nextChar()
            return True
        return False

    def uppercase_char(self):
        """<uppercase-char> -> A | B | C | ... | Z | _"""
        if self.lex.getToken() == Token.UPPERCASE:
            self.lex.nextChar()
            return True
        return False

    def digit(self):
        """<digit> -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9"""
        if self.lex.getToken() == Token.DIGIT:
            self.lex.nextChar()
            return True
        return False

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

    def predicate_list(self):
        """<predicate-list> -> <predicate> | <predicate> , <predicate-list>"""
        if not self.predicate():
            return False

        char = self.lex.getToken()
        if char == Token.COMMA:
            self.lex.nextChar()
            return self.predicate_list()
        return True

    def term_list(self):
        """<term-list> -> <term> | <term> , <term-list>"""
        if not self.term():
            return False

        char = self.lex.getToken()
        if char == Token.COMMA:
            self.lex.nextChar()
            return self.term_list()
        return True

    def term(self):
        """<term> -> <atom> | <variable> | <structure> | <numeral>"""
        save_position = self.lex.getPosition()

        # Try atom first (which might be part of a structure)
        if self.atom():
            if self.lex.getToken() == Token.LPAREN:  # This is actually a structure
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

        if self.lex.getToken() != Token.LPAREN:
            return False
        self.lex.nextChar()

        if not self.term_list():
            return False

        if self.lex.getToken() != Token.RPAREN:
            self.err.syntax_error("Expected ')' after term list")
            return False
        self.lex.nextChar()
        return True

    def atom(self):
        """<atom> -> <small-atom> | ' <string> '"""
        char = self.lex.getToken()
        if char == Token.QUOTE:
            self.lex.nextChar()
            if not self.string():
                return False
            if self.lex.getToken() != Token.QUOTE:
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
        next_char = self.lex.getToken()
        if next_char and next_char != Token.QUOTE:
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
        char = self.lex.getToken()
        if char == Token.SPECIAL:
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


def parse_file(filename):
    try:
        with open(filename, "r") as f:
            input_lines = f.readlines()

        print()
        print(f"Parsing {filename}")
        lexical = LexicalAnalyzer(input_lines)
        error = ErrorHandler(lexical)
        syntax = SyntaxAnalyzer(lexical, error)

        e = syntax.parse()
        if e:
            print("Program parsed with no errors")
        else:
            error.report_errors()

        return True  # File was found and parsed (regardless of errors)

    except FileNotFoundError:
        return False  # File was not found


# copied from https://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting
# to redirect print to both stdout and console
import sys


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("parser_output.txt", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass


sys.stdout = Logger()


def main():
    program_num = 1
    files_parsed = 0

    while True:
        filename = f"{program_num}.txt"
        if parse_file(filename):
            files_parsed += 1
        else:
            break
        program_num += 1

    print(f"\nParsing complete. Total files parsed: {files_parsed}")


if __name__ == "__main__":
    main()
