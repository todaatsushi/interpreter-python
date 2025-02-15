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
