# Prolog Parser

**Programming Languages (CMP321) Project**
This project involves creating a parser for a subset of Prolog. The grammar used in this parser is outlined below.

---

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
