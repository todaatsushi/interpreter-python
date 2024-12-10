from monkey.interpreter import environment, parsers, evaluate, lexers


class Repl:
    PROMPT = ">>>> "

    def start(self) -> None:
        while True:
            line = input(self.PROMPT)
            parsed = line.strip().split(self.PROMPT)[0].strip()
            print(run(parsed))


def run(code: str) -> str:
    lexer = lexers.Lexer.new(code)
    parser = parsers.Parser.new(lexer)
    program = parser.parse_program()

    if not parser.errors:
        env = environment.Environment()
        return_value = evaluate.node(program, env)
        if return_value:
            return return_value.inspect()
        return ""
    else:
        return "\n".join(parser.errors)
