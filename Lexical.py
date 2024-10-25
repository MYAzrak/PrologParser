class LexicalAnalyser:
    def __init__(self, program):
        self.line = 0
        self.position = 0
        self.input_lines = program

    def getChar(self):
        return self.input_lines[self.line][self.position]

    def nextChar(self):

        if self.position < len(self.input_lines[self.line])-1:
            self.position += 1
        else:
            self.line += 1
            self.position = 0

        if self.line >= len(self.input_lines):
            return ''
        else:
            if self.getChar() == '\n':
                return self.nextChar()
        return self.getChar()
