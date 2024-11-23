import enum

Token = enum.Enum(
    "Token",
    [
        "LETTER",
        "DIGIT",
        "UNKNOWN",
        "PERIOD",  # .
        "QUESTION",  # ?-
        "IMPLIES",  # :-
        "COMMA",  # ,
        "LPAREN",  # (
        "RPAREN",  # )
        "QUOTE",  # '
        "SMALL_ATOM",  # lowercase identifiers
        "VARIABLE",  # uppercase identifiers
        "STRING",  # quoted strings
        "NUMERAL",  # numbers
        "SPECIAL",  # special characters
        "EOF",  # end of file
    ],
)


class LexicalAnalyzer:
    def __init__(self):
        self.charClass = 0
        self.lexeme = [""] * 100  # Array to store lexeme
        self.nextChar = ""
        self.nextToken = 0
        self.lexLen = 0
        self.token = 0

    def getChar(self, input_string, position):
        """Gets the next character of input and determine its character class"""
        if position < len(input_string):
            self.nextChar = input_string[position]

            # Determine character class
            if self.nextChar.isupper() or self.nextChar == "_":  # <uppercase-char>
                self.charClass = Token.LETTER
            elif self.nextChar.islower():  # <lowercase-char>
                self.charClass = Token.LETTER
            elif self.nextChar.isdigit():  # <digit>
                self.charClass = Token.DIGIT
            else:
                self.charClass = Token.UNKNOWN
        else:
            self.charClass = Token.EOF
            self.nextChar = ""

        return position + 1

    def addChar(self):
        """Add nextChar to lexeme"""
        if self.lexLen < 98:  # Leave room for null terminator
            self.lexeme[self.lexLen] = self.nextChar
            self.lexLen += 1
            self.lexeme[self.lexLen] = ""  # Null terminate the string
        else:
            print("Error - lexeme is too long")

    def getNonBlank(self, input_string, position):
        """Call getChar until it returns a non-whitespace character"""
        while self.nextChar.isspace():
            position = self.getChar(input_string, position)
        return position

    def lookup(self, ch):
        """Lookup operators and parentheses and return the token"""
        if ch == ".":
            self.addChar()
            self.nextToken = Token.PERIOD
        elif ch == ",":
            self.addChar()
            self.nextToken = Token.COMMA
        elif ch == "(":
            self.addChar()
            self.nextToken = Token.LPAREN
        elif ch == ")":
            self.addChar()
            self.nextToken = Token.RPAREN
        elif ch == "'":
            self.addChar()
            self.nextToken = Token.QUOTE
        else:
            self.addChar()
            self.nextToken = Token.EOF
        return self.nextToken

    def lex(self, input_string, position):
        self.lexLen = 0
        position = self.getNonBlank(input_string, position)

        match self.charClass:
            case Token.LETTER:
                # Handle identifiers (both SMALL_ATOM and VARIABLE)
                self.addChar()
                position = self.getChar(input_string, position)
                while self.charClass == Token.LETTER or self.charClass == Token.DIGIT:
                    self.addChar()
                    position = self.getChar(input_string, position)
                if self.lexeme[0].isupper() or self.lexeme[0] == "_":
                    self.nextToken = Token.VARIABLE
                else:
                    self.nextToken = Token.SMALL_ATOM

            case Token.DIGIT:
                # Handle numbers
                self.addChar()
                position = self.getChar(input_string, position)
                while self.charClass == Token.DIGIT:
                    self.addChar()
                    position = self.getChar(input_string, position)
                self.nextToken = Token.NUMERAL

            case Token.UNKNOWN:
                # Handle special two-character tokens and other special characters
                if (
                    self.nextChar == "?"
                    and position < len(input_string)
                    and input_string[position] == "-"
                ):
                    self.addChar()  # add ?
                    position = self.getChar(input_string, position)
                    self.addChar()  # add -
                    position = self.getChar(input_string, position)
                    self.nextToken = Token.QUESTION
                elif (
                    self.nextChar == ":"
                    and position < len(input_string)
                    and input_string[position] == "-"
                ):
                    self.addChar()  # add :
                    position = self.getChar(input_string, position)
                    self.addChar()  # add -
                    position = self.getChar(input_string, position)
                    self.nextToken = Token.IMPLIES
                else:
                    self.lookup(self.nextChar)
                    position = self.getChar(input_string, position)

            case EOF:
                self.nextToken = EOF
                self.lexeme[0] = "E"
                self.lexeme[1] = "O"
                self.lexeme[2] = "F"
                self.lexeme[3] = "\0"

        print(
            f"Next token is: {self.nextToken}, Next lexeme is {''.join(self.lexeme[:self.lexLen])}"
        )
        return position, self.nextToken


# Example usage
def analyze(lex_analyzer, input_string):
    position = 0
    position = lex_analyzer.getChar(input_string, position)

    while True:
        position, token = lex_analyzer.lex(input_string, position)
        if token == Token.EOF:
            break
