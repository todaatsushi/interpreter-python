from monkey.interpreter import ast, lexers, parsers


def read_script(filename: str) -> str:
    script = ""
    with open(filename) as file:
        for line in file.readlines():
            script = f"{script}\n{line.strip('\n')}"
    script = script.strip()
    return script


def parse(code: str) -> ast.Program:
    lexer = lexers.Lexer.new(code)
    parser = parsers.Parser.new(lexer)
    program = parser.parse_program()
    if parser.errors:
        raise Exception(["\n".join(e for e in parser.errors)])
    return program
