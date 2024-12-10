from monkey.interpreter import environment, lexers, parsers, evaluate


class Scanner:
    PROMPT = ">>>> "

    def start(self) -> None:
        env = environment.Environment()
        while True:
            line = input(self.PROMPT)
            parsed = line.strip().split(self.PROMPT)[0].strip()
            lexer = lexers.Lexer.new(parsed)
            parser = parsers.Parser.new(lexer)

            program = parser.parse_program()

            if not parser.errors:
                return_value = evaluate.node(program, env)
                if return_value:
                    print(return_value.inspect())
            else:
                print("\n".join(parser.errors))
