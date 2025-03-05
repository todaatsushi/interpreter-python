from unittest import TestCase

from monkey.compiler import symbol_table as st


class TestSymbolTable(TestCase):
    def test_define(self) -> None:
        expected: dict[str, st.Symbol] = {
            "a": st.Symbol("a", st.Scope.GLOBAL, 0),
            "b": st.Symbol("b", st.Scope.GLOBAL, 1),
        }

        global_scope = st.SymbolTable.new()

        actual_a = global_scope.define("a")
        self.assertEqual(expected["a"], actual_a)
        self.assertEqual(global_scope.num_definitions, 1)

        actual_b = global_scope.define("b")
        self.assertEqual(expected["b"], actual_b)
        self.assertEqual(global_scope.num_definitions, 2)

    def test_resolve(self) -> None:
        expected: dict[str, st.Symbol] = {
            "a": st.Symbol("a", st.Scope.GLOBAL, 0),
            "b": st.Symbol("b", st.Scope.GLOBAL, 1),
        }

        global_scope = st.SymbolTable.new()
        global_scope.store["a"] = expected["a"]
        global_scope.store["b"] = expected["b"]

        actual_a = global_scope.resolve("a")
        self.assertEqual(expected["a"], actual_a)

        actual_b = global_scope.resolve("b")
        self.assertEqual(expected["b"], actual_b)

    def test_define_resolve_builtins(self) -> None:
        global_ = st.SymbolTable.new()
        first_local = st.SymbolTable.new_enclosed(global_)
        second_local = st.SymbolTable.new_enclosed(first_local)

        expected_symbols = [
            st.Symbol(name="a", scope=st.Scope.BUILTIN, index=0),
            st.Symbol(name="b", scope=st.Scope.BUILTIN, index=1),
            st.Symbol(name="c", scope=st.Scope.BUILTIN, index=2),
            st.Symbol(name="d", scope=st.Scope.BUILTIN, index=3),
        ]

        for i, expected in enumerate(expected_symbols):
            global_.define_builtin(i, expected.name)

        for table in [global_, first_local, second_local]:
            for expected in expected_symbols:
                try:
                    actual = table.resolve(expected.name)
                except st.MissingDefinition:
                    self.fail(f"Missing definition for {expected}")

                self.assertEqual(actual, expected)

    def test_resolve_free(self) -> None:
        global_scope = st.SymbolTable.new()
        global_scope.define("a")
        global_scope.define("b")

        first_local = st.SymbolTable.new_enclosed(global_scope)
        first_local.define("c")
        first_local.define("d")

        second_local = st.SymbolTable.new_enclosed(first_local)
        second_local.define("e")
        second_local.define("f")

        tests: tuple[tuple[st.SymbolTable, list[st.Symbol], list[st.Symbol]], ...] = (
            (
                first_local,
                [
                    st.Symbol(name="a", scope=st.Scope.GLOBAL, index=0),
                    st.Symbol(name="b", scope=st.Scope.GLOBAL, index=1),
                    st.Symbol(name="c", scope=st.Scope.LOCAL, index=0),
                    st.Symbol(name="d", scope=st.Scope.LOCAL, index=1),
                ],
                [],
            ),
            (
                second_local,
                [
                    st.Symbol(name="a", scope=st.Scope.GLOBAL, index=0),
                    st.Symbol(name="b", scope=st.Scope.GLOBAL, index=1),
                    st.Symbol(name="c", scope=st.Scope.FREE, index=0),
                    st.Symbol(name="d", scope=st.Scope.FREE, index=1),
                    st.Symbol(name="e", scope=st.Scope.LOCAL, index=0),
                    st.Symbol(name="f", scope=st.Scope.LOCAL, index=1),
                ],
                [
                    st.Symbol(name="c", scope=st.Scope.LOCAL, index=0),
                    st.Symbol(name="d", scope=st.Scope.LOCAL, index=1),
                ],
            ),
        )

        for i, (symbol_table, expected_symbols, expected_free_symbols) in enumerate(
            tests
        ):
            with self.subTest(f"Free scope test: {i}"):
                for expected_symbol in expected_symbols:
                    try:
                        actual_symbol = symbol_table.resolve(expected_symbol.name)
                    except st.MissingDefinition:
                        self.fail(
                            f"Missing definition: {expected_symbol.name} in {symbol_table}"
                        )

                    self.assertEqual(actual_symbol, expected_symbol)

                self.assertEqual(
                    len(symbol_table.free_symbols), len(expected_free_symbols)
                )

                for i, expected_free_symbol in enumerate(expected_free_symbols):
                    actual_free_symbol = symbol_table.free_symbols[i]
                    self.assertEqual(actual_free_symbol, expected_free_symbol)

    def test_resolve_unresolvable_free(self) -> None:
        global_scope = st.SymbolTable.new()
        global_scope.define("a")

        first_local = st.SymbolTable.new_enclosed(global_scope)
        first_local.define("c")

        second_local = st.SymbolTable.new_enclosed(first_local)
        second_local.define("e")
        second_local.define("f")

        expected: list[st.Symbol] = [
            st.Symbol(name="a", scope=st.Scope.GLOBAL, index=0),
            st.Symbol(name="c", scope=st.Scope.FREE, index=0),
            st.Symbol(name="e", scope=st.Scope.LOCAL, index=0),
            st.Symbol(name="f", scope=st.Scope.LOCAL, index=1),
        ]

        for expected_symbol in expected:
            actual_symbol = second_local.resolve(expected_symbol.name)
            self.assertEqual(actual_symbol, expected_symbol)

        expected_unresolvable = ["b", "d"]
        for name in expected_unresolvable:
            try:
                second_local.resolve(name)
            except st.MissingDefinition:
                pass
            else:
                self.fail(f"Didn't expect to resolve '{name}' in {second_local}")
