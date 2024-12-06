from interpreter import lexers, parsers


class Scanner:
    PROMPT = ">>>> "

    def start(self) -> None:
        while True:
            line = input(self.PROMPT)
            parsed = line.strip().split(self.PROMPT)[0].strip()
            lexer = lexers.Lexer.new(parsed)
            parser = parsers.Parser.new(lexer)

            program = parser.parse_program()

            if not parser.errors:
                print(program)
            else:
                print("\n".join(parser.errors))
