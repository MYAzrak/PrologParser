from Syntax import SyntaxAnalyser
from Lexical import LexicalAnalyser
from Errors import ErrorHandler


def parse_file(filename):
    try:
        with open(filename, 'r') as f:
            input_lines = f.readlines()

        print(f"Parsing {filename}")
        lexical = LexicalAnalyser(input_lines)
        error = ErrorHandler()
        syntax = SyntaxAnalyser(lexical, error)

        syntax.parse()
        error.report_errors()

        return True  # File was found and parsed (regardless of errors)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return False  # File was not found


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
