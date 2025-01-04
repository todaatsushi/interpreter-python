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
