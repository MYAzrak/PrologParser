# Prolog Parser

This project involves creating a parser for a subset of Prolog using Python. The grammar used in this parser is outlined below. The parser consists of two main components: a lexical analyzer and a syntax analyzer.

## Lexical Analyzer

The lexical analyzer processes input sentences by dividing them into tokens. It detects components like letters, numbers, operators, and special symbols. These identified tokens are categorized in the Token enumeration.

## Syntax Analyzer

The syntax analyzer ensures the correctness of assignment statement structures. Using tokens and lexemes provided by the lexical analyzer, it enforces adherence to the defined grammar rules. When the input deviates from these rules, the parser identifies the errors and generates appropriate error messages.

## Grammar

The grammar defines the structure of valid Prolog programs and queries as follows:

- `<program> -> <clause-list> <query> | <query>`
- `<clause-list> -> <clause> | <clause> <clause-list>`
- `<clause> -> <predicate> . | <predicate> :- <predicate-list> .`
- `<query> -> ?- <predicate-list> .`
- `<predicate-list> -> <predicate> | <predicate> , <predicate-list>`
- `<predicate> -> <atom> | <atom> ( <term-list> )`
- `<term-list> -> <term> | <term> , <term-list>`
- `<term> -> <atom> | <variable> | <structure> | <numeral>`
- `<structure> -> <atom> ( <term-list> )`
- `<atom> -> <small-atom> | ' <string> '`
- `<small-atom> -> <lowercase-char> | <lowercase-char> <character-list>`
- `<variable> -> <uppercase-char> | <uppercase-char> <character-list>`
- `<character-list> -> <alphanumeric> | <alphanumeric> <character-list>`
- `<alphanumeric> -> <lowercase-char> | <uppercase-char> | <digit>`
- `<lowercase-char> -> a | b | c | ... | x | y | z`
- `<uppercase-char> -> A | B | C | ... | X | Y | Z | _`
- `<numeral> -> <digit> | <digit> <numeral>`
- `<digit> -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9`
- `<string> -> <character> | <character> <string>`
- `<character> -> <alphanumeric> | <special>`
- `<special> -> + | - | * | / | \ | ^ | ~ | : | . | ? | | # | $ | &`

## How to Run

1. Ensure that there are sequentially numbered text files named '1', '2', and so on, present in the same directory as the parser.py. The text files should contain the sentences to be parsed, there can be more than one sentence in each file.
2. Run parser.py.
3. parser_output.txt will be generated and will contain the error details.
