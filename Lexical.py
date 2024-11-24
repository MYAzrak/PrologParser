class LexicalAnalyzer:
    def __init__(self, program):
        self.line = 0
        self.position = 0
        self.input_lines = program

    def getChar(self, keep_space = False):
        c = self.input_lines[self.line][self.position]
        if keep_space and c == " ":
            return c
        elif c == " ":
            return self.nextChar()
        else:
            return c

    def nextChar(self):
        if self.position < len(self.input_lines[self.line]) - 1:
            self.position += 1
        else:
            self.line += 1
            self.position = 0

        if self.line >= len(self.input_lines):
            return ""
        else:
            if self.getChar() == "\n":
                return self.nextChar()

        return self.getChar()

    def getPosition(self):
        return self.line, self.position

    def setPosition(self, line, position):
        self.line = line
        self.position = position
    
    def getLine(self):
        return self.input_lines[self.line]
