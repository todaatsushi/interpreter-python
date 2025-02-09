import unittest

from collections.abc import Mapping, Sequence

from monkey.compiler import code, compilers, symbol_table as st
from monkey.interpreter import objects
from tests import utils


def run_compiler_tests(
    tc: unittest.TestCase,
    test_cases: tuple[tuple[str, list[object], list[code.Instructions]], ...],
) -> None:
    for input_, expected_constants, expected_instructions in test_cases:
        with tc.subTest(input_):
            program = utils.parse(input_)
            compiler = compilers.Compiler.new()

            try:
                compiler.compile(program)
            except compilers.CouldntCompile as exc:
                tc.fail(
                    f"Couldn't compile program{': ' + str(exc) if str(exc) else '.'}"
                )

            bytecode = compiler.bytecode()

            with tc.subTest(f"{input_}: instructions"):
                test_instructions(tc, expected_instructions, bytecode.instructions)

            with tc.subTest(f"{input_}: constants"):
                test_constants(tc, expected_constants, bytecode.constants)


def test_constants(
    tc: unittest.TestCase, expected: list[object], actual: list[objects.Object]
) -> None:
    tc.assertEqual(
        len(expected),
        len(actual),
        f"Expected {len(expected)} bytes, got:\n\n{expected}\n\nvs\n\n{actual}",
    )

    for i, exp in enumerate(expected):
        if isinstance(exp, int):
            tc.assertIsInstance(actual[i], objects.Integer)
            assert isinstance(actual[i], objects.Integer)

            tc.assertEqual(actual[i].value, exp)
        elif isinstance(exp, str):
            tc.assertIsInstance(actual[i], objects.String)
            assert isinstance(actual[i], objects.String)

            tc.assertEqual(actual[i].value, exp)
        elif isinstance(exp, code.Instructions):
            func = actual[i]
            tc.assertIsInstance(func, objects.CompiledFunction)
            assert isinstance(func, objects.CompiledFunction)

            test_instructions(tc, [exp], func.instructions)
        elif isinstance(exp, list):
            func = actual[i]
            tc.assertIsInstance(func, objects.CompiledFunction)
            assert isinstance(func, objects.CompiledFunction)

            test_instructions(tc, exp, func.instructions)
        else:
            tc.fail(f"{type(exp)} not supported")


def test_instructions(
    tc: unittest.TestCase,
    expected: list[code.Instructions],
    actual: code.Instructions,
) -> None:
    all_instructions = code.Instructions.concat_bytes(expected)
    tc.assertEqual(
        len(actual),
        len(all_instructions),
        f"Expected {len(all_instructions)} bytes, expected:\n\n{all_instructions}\n\nvs\n\n{actual}",
    )

    for i, instruction in enumerate(all_instructions):
        tc.assertEqual(
            instruction,
            actual[i],
            f"Expected '{instruction}' at position {i}, got '{actual[i]}'\n\nGot:\n\n{str(actual)}\n\nExpected:\n\n{str(all_instructions)}",
        )


class TestCompiler(unittest.TestCase):
    def test_integers_arithmetic(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "1 + 2",
                    [1, 2],
                    [
                        *[code.make(code.OpCodes.CONSTANT, i) for i in range(2)],
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 - 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.SUBTRACT),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 * 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.MULTIPLY),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 / 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.DIVIDE),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "-1",
                    [1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.MINUS),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_expression_pops(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    ("1; 2"),
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.POP),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_boolean_expressions(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "true",
                    [],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "false",
                    [],
                    [
                        code.make(code.OpCodes.FALSE),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 > 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.GREATER_THAN),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 < 2",
                    [2, 1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.GREATER_THAN),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 == 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.EQUAL),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "1 != 2",
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.NOT_EQUAL),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "true == false",
                    [],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.FALSE),
                        code.make(code.OpCodes.EQUAL),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "true != false",
                    [],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.FALSE),
                        code.make(code.OpCodes.NOT_EQUAL),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "!true",
                    [],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.EXCLAIMATION_MARK),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_conditionals(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "if (true) { 10 }; 3333;",
                    [10, 3333],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.JUMP_NOT_TRUTHY, 10),
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.JUMP, 11),
                        code.make(code.OpCodes.NULL),
                        code.make(code.OpCodes.POP),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "if (true) { 10 } else {20}; 3333;",
                    [10, 20, 3333],
                    [
                        code.make(code.OpCodes.TRUE),
                        code.make(code.OpCodes.JUMP_NOT_TRUTHY, 10),
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.JUMP, 13),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.POP),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_global_let_statements(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    ("let one = 1;\nlet two = 2;"),
                    [1, 2],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.SET_GLOBAL, 1),
                    ],
                ),
                (
                    "let one = 1;\n one;",
                    [1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.GET_GLOBAL, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "let one = 1;\nlet two = one;\ntwo;",
                    [1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.GET_GLOBAL, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 1),
                        code.make(code.OpCodes.GET_GLOBAL, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_local_let_statements(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "let num = 55;\n" "fn() { num }",
                    [
                        55,
                        [
                            code.make(code.OpCodes.GET_GLOBAL, 0),
                            code.make(code.OpCodes.RETURN_VALUE),
                        ],
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "fn() { let num = 55; num }",
                    [
                        55,
                        [
                            code.make(code.OpCodes.CONSTANT, 0),
                            code.make(code.OpCodes.SET_LOCAL, 0),
                            code.make(code.OpCodes.GET_LOCAL, 0),
                            code.make(code.OpCodes.RETURN_VALUE),
                        ],
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "fn() { let a = 55; let b = 77; a + b }",
                    [
                        55,
                        77,
                        [
                            code.make(code.OpCodes.CONSTANT, 0),
                            code.make(code.OpCodes.SET_LOCAL, 0),
                            code.make(code.OpCodes.CONSTANT, 1),
                            code.make(code.OpCodes.SET_LOCAL, 1),
                            code.make(code.OpCodes.GET_LOCAL, 0),
                            code.make(code.OpCodes.GET_LOCAL, 1),
                            code.make(code.OpCodes.ADD),
                            code.make(code.OpCodes.RETURN_VALUE),
                        ],
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_resolve_local(self) -> None:
        global_ = st.SymbolTable.new()
        global_.define("a")
        global_.define("b")

        first_local = st.SymbolTable.new_enclosed(global_)
        first_local.define("c")
        first_local.define("d")

        second_local = st.SymbolTable.new_enclosed(first_local)
        second_local.define("e")
        second_local.define("f")

        tests: Sequence[tuple[str, st.SymbolTable, Sequence[st.Symbol]]] = (
            (
                "first_local",
                first_local,
                (
                    st.Symbol("a", st.Scope.GLOBAL, 0),
                    st.Symbol("b", st.Scope.GLOBAL, 1),
                    st.Symbol("c", st.Scope.LOCAL, 0),
                    st.Symbol("d", st.Scope.LOCAL, 1),
                ),
            ),
            (
                "second_local",
                second_local,
                (
                    st.Symbol("a", st.Scope.GLOBAL, 0),
                    st.Symbol("b", st.Scope.GLOBAL, 1),
                    st.Symbol("e", st.Scope.LOCAL, 0),
                    st.Symbol("f", st.Scope.LOCAL, 1),
                ),
            ),
        )

        for type_, symbol_table, symbols in tests:
            with self.subTest(type_):
                for symbol in symbols:
                    try:
                        result = symbol_table.resolve(symbol.name)
                    except st.MissingDefinition:
                        self.assertTrue(
                            False, f"Missing definition for {symbol} in {symbol_table}"
                        )
                        assert False, "Unreachable"

                    self.assertEqual(symbol, result)

    def test_string(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    '"monkey"',
                    ["monkey"],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    '"mon" + "key"',
                    ["mon", "key"],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_array(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "[]",
                    [],
                    [
                        code.make(code.OpCodes.ARRAY, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "[1, 2, 3]",
                    [1, 2, 3],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.ARRAY, 3),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "[1 + 2, 3 - 4, 5 * 6]",
                    [1, 2, 3, 4, 5, 6],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.SUBTRACT),
                        code.make(code.OpCodes.CONSTANT, 4),
                        code.make(code.OpCodes.CONSTANT, 5),
                        code.make(code.OpCodes.MULTIPLY),
                        code.make(code.OpCodes.ARRAY, 3),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_hash_map(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "{}",
                    [],
                    [
                        code.make(code.OpCodes.HASH, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "{1: 2, 3: 4, 5: 6}",
                    [1, 2, 3, 4, 5, 6],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.CONSTANT, 4),
                        code.make(code.OpCodes.CONSTANT, 5),
                        code.make(code.OpCodes.HASH, 6),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "{1: 2 + 3, 4: 5 * 6}",
                    [1, 2, 3, 4, 5, 6],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.CONSTANT, 4),
                        code.make(code.OpCodes.CONSTANT, 5),
                        code.make(code.OpCodes.MULTIPLY),
                        code.make(code.OpCodes.HASH, 4),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_index_expressions(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "[1, 2, 3][1 + 1]",
                    [1, 2, 3, 1, 1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.ARRAY, 3),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.CONSTANT, 4),
                        code.make(code.OpCodes.ADD),
                        code.make(code.OpCodes.INDEX),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "{1: 2}[2 - 1]",
                    [1, 2, 2, 1],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.HASH, 2),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.SUBTRACT),
                        code.make(code.OpCodes.INDEX),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_compiler_scopes(self) -> None:
        compiler = compilers.Compiler.new()
        self.assertEqual(compiler.scope_index, 0)

        global_symbol_table = compiler.symbol_table

        compiler.emit(code.OpCodes.MULTIPLY)
        self.assertEqual(len(compiler.scopes[compiler.scope_index].instructions), 1)

        compiler.enter_scope()
        self.assertEqual(compiler.scope_index, 1)

        compiler.emit(code.OpCodes.SUBTRACT)
        current_scope = compiler.scopes[compiler.scope_index]
        self.assertEqual(len(current_scope.instructions), 1)

        latest_instruction = current_scope.last_instruction
        self.assertIsNotNone(latest_instruction)
        assert latest_instruction is not None
        self.assertEqual(latest_instruction.op_code, code.OpCodes.SUBTRACT)

        self.assertIs(compiler.symbol_table.outer, global_symbol_table)

        compiler.leave_scope()
        self.assertEqual(compiler.scope_index, 0)

        self.assertIs(compiler.symbol_table, global_symbol_table)
        self.assertIsNone(compiler.symbol_table.outer)

        compiler.emit(code.OpCodes.ADD)
        current_scope = compiler.scopes[compiler.scope_index]
        self.assertEqual(len(current_scope.instructions), 2)

        latest_instruction = current_scope.last_instruction
        self.assertIsNotNone(latest_instruction)
        assert latest_instruction is not None
        self.assertEqual(latest_instruction.op_code, code.OpCodes.ADD)

        previous_instruction = current_scope.previous_instruction
        self.assertIsNotNone(previous_instruction)
        assert previous_instruction is not None
        self.assertEqual(previous_instruction.op_code, code.OpCodes.MULTIPLY)

    def test_functions(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "fn() { return 5 + 10 }",
                    [
                        5,
                        10,
                        code.Instructions.concat_bytes(
                            [
                                code.make(code.OpCodes.CONSTANT, 0),
                                code.make(code.OpCodes.CONSTANT, 1),
                                code.make(code.OpCodes.ADD),
                                code.make(code.OpCodes.RETURN_VALUE),
                            ]
                        ),
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "fn() { 5 + 10 }",
                    [
                        5,
                        10,
                        code.Instructions.concat_bytes(
                            [
                                code.make(code.OpCodes.CONSTANT, 0),
                                code.make(code.OpCodes.CONSTANT, 1),
                                code.make(code.OpCodes.ADD),
                                code.make(code.OpCodes.RETURN_VALUE),
                            ]
                        ),
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "fn() { 1; 2 }",
                    [
                        1,
                        2,
                        code.Instructions.concat_bytes(
                            [
                                code.make(code.OpCodes.CONSTANT, 0),
                                code.make(code.OpCodes.POP),
                                code.make(code.OpCodes.CONSTANT, 1),
                                code.make(code.OpCodes.RETURN_VALUE),
                            ]
                        ),
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "fn() {}",
                    [
                        code.Instructions.concat_bytes(
                            [code.make(code.OpCodes.RETURN)]
                        ),
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_function_calls(self) -> None:
        run_compiler_tests(
            self,
            (
                (
                    "fn() { 24 }();",
                    [
                        24,
                        code.Instructions.concat_bytes(
                            [
                                code.make(code.OpCodes.CONSTANT, 0),  # Function value
                                code.make(code.OpCodes.RETURN_VALUE),
                            ]
                        ),
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 1),  # Actual function
                        code.make(code.OpCodes.CALL, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "let noArg = fn() { 24 }; \nnoArg();",
                    [
                        24,
                        code.Instructions.concat_bytes(
                            [
                                code.make(code.OpCodes.CONSTANT, 0),  # Function value
                                code.make(code.OpCodes.RETURN_VALUE),
                            ]
                        ),
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 1),  # Actual function
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.GET_GLOBAL, 0),
                        code.make(code.OpCodes.CALL, 0),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "let oneArg = fn(a) { a }; \noneArg(24);",
                    [
                        code.Instructions.concat_bytes(
                            [
                                code.make(code.OpCodes.GET_LOCAL, 0),
                                code.make(code.OpCodes.RETURN_VALUE),
                            ]
                        ),
                        24,
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.GET_GLOBAL, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CALL, 1),
                        code.make(code.OpCodes.POP),
                    ],
                ),
                (
                    "let manyArg = fn(a, b, c) { a; b; c; };\n manyArg(24, 25, 26);",
                    [
                        code.Instructions.concat_bytes(
                            [
                                code.make(code.OpCodes.GET_LOCAL, 0),
                                code.make(code.OpCodes.POP),
                                code.make(code.OpCodes.GET_LOCAL, 1),
                                code.make(code.OpCodes.POP),
                                code.make(code.OpCodes.GET_LOCAL, 2),
                                code.make(code.OpCodes.RETURN_VALUE),
                            ]
                        ),
                        24,
                        25,
                        26,
                    ],
                    [
                        code.make(code.OpCodes.CONSTANT, 0),
                        code.make(code.OpCodes.SET_GLOBAL, 0),
                        code.make(code.OpCodes.GET_GLOBAL, 0),
                        code.make(code.OpCodes.CONSTANT, 1),
                        code.make(code.OpCodes.CONSTANT, 2),
                        code.make(code.OpCodes.CONSTANT, 3),
                        code.make(code.OpCodes.CALL, 3),
                        code.make(code.OpCodes.POP),
                    ],
                ),
            ),
        )

    def test_define_symbol_table(self) -> None:
        expected: Mapping[str, st.Symbol] = {
            "a": st.Symbol("a", st.Scope.GLOBAL, 0),
            "b": st.Symbol("b", st.Scope.GLOBAL, 1),
            "c": st.Symbol("c", st.Scope.LOCAL, 0),
            "d": st.Symbol("d", st.Scope.LOCAL, 1),
            "e": st.Symbol("e", st.Scope.LOCAL, 0),
            "f": st.Symbol("f", st.Scope.LOCAL, 1),
        }

        global_ = st.SymbolTable.new()

        a = global_.define("a")
        self.assertEqual(a, expected["a"])

        b = global_.define("b")
        self.assertEqual(b, expected["b"])

        first_local = st.SymbolTable.new_enclosed(global_)

        c = first_local.define("c")
        self.assertEqual(c, expected["c"])

        d = first_local.define("d")
        self.assertEqual(d, expected["d"])

        second_local = st.SymbolTable.new_enclosed(first_local)

        e = second_local.define("e")
        self.assertEqual(e, expected["e"])

        f = second_local.define("f")
        self.assertEqual(f, expected["f"])
