import enum
from monkey.compiler import compilers, vm
from monkey.interpreter import environment, parsers, evaluate, lexers


class RunType(enum.StrEnum):
    INTERPRETER = "interpreter"
    COMPILED = "vm"


class Repl:
    PROMPT = ">>>> "

    def start(self, run_type: RunType) -> None:
        while True:
            line = input(self.PROMPT)
            parsed = line.strip().split(self.PROMPT)[0].strip()
            print(run(parsed, run_type))


class Script:
    def eval(self, filename: str, run_type: RunType) -> None:
        with open(filename) as f:
            code = f.read()
            print(run(code, run_type))


def run(code: str, run_type: RunType) -> str:
    lexer = lexers.Lexer.new(code)
    parser = parsers.Parser.new(lexer)
    program = parser.parse_program()

    if parser.errors:
        return "\n".join(parser.errors)

    if run_type == RunType.INTERPRETER:
        env = environment.Environment()
        return_value = evaluate.node(program, env)
        if return_value:
            return return_value.inspect()
    else:
        compiler = compilers.Compiler.new()
        compiler.compile(program)
        machine = vm.VM.from_bytecode(compiler.bytecode())
        machine.run()
        print(machine.last_popped_stack_elem.inspect())

    return ""
