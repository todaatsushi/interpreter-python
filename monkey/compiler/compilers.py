from __future__ import annotations

import dataclasses as dc

from monkey.compiler import code, symbol_table as st
from monkey.interpreter import ast
from monkey.interpreter import objects


FAKE_JUMP_VALUE = 9999


class CompilerError(Exception):
    pass


class CouldntCompile(CompilerError):
    pass


@dc.dataclass(kw_only=True, frozen=True)
class EmittedInstruction:
    op_code: code.OpCodes
    position: int


@dc.dataclass
class CompilationScope:
    instructions: code.Instructions = dc.field(default_factory=code.Instructions)
    last_instruction: EmittedInstruction | None = None
    previous_instruction: EmittedInstruction | None = None


@dc.dataclass
class Bytecode:
    instructions: code.Instructions = dc.field(default_factory=code.Instructions)
    constants: list[objects.Object] = dc.field(default_factory=list)


@dc.dataclass
class Compiler:
    symbol_table: st.SymbolTable

    scopes: list[CompilationScope]
    scope_index: int

    constants: list[objects.Object] = dc.field(init=False, default_factory=list)

    @classmethod
    def new(cls, symbol_table: st.SymbolTable | None = None) -> Compiler:
        main_scope = CompilationScope()
        _symbol_table = symbol_table or st.SymbolTable.new()

        for i, name in enumerate(objects.BUILTIN_MAP):
            _symbol_table.define_builtin(i, name)

        return cls(
            symbol_table=_symbol_table,
            scopes=[main_scope],
            scope_index=0,
        )

    # Scope
    def enter_scope(self) -> None:
        scope = CompilationScope()

        enclosed_symbol_table = st.SymbolTable.new_enclosed(self.symbol_table)
        self.symbol_table = enclosed_symbol_table

        self.scopes.append(scope)
        self.scope_index += 1

    def leave_scope(self) -> code.Instructions:
        instructions = self.current_scope.instructions

        assert self.symbol_table.outer
        self.symbol_table = self.symbol_table.outer

        self.scopes.pop()
        self.scope_index -= 1

        return instructions

    # Symbol table
    def load_symbol(self, symbol: st.Symbol):
        match symbol.scope:
            case st.Scope.GLOBAL:
                op_code = code.OpCodes.GET_GLOBAL
            case st.Scope.LOCAL:
                op_code = code.OpCodes.GET_LOCAL
            case st.Scope.BUILTIN:
                op_code = code.OpCodes.GET_BUILTIN
            case st.Scope.FREE:
                op_code = code.OpCodes.GET_FREE
        self.emit(op_code, symbol.index)

    @property
    def current_scope(self) -> CompilationScope:
        return self.scopes[self.scope_index]

    # Instructions
    def _add_constant(self, o: objects.Object) -> int:
        """Returns position"""
        self.constants.append(o)
        return len(self.constants) - 1

    def _add_instruction(self, instruction: code.Instructions) -> int:
        """Returns position"""
        current_instructions = self.current_scope.instructions
        new_instruction_position = len(current_instructions)

        updated_instructions = current_instructions.concat_bytes(
            [current_instructions, instruction]
        )
        self.current_scope.instructions = updated_instructions

        return new_instruction_position

    def _set_last_instruction(self, op_code: code.OpCodes, position: int) -> None:
        previous = self.current_scope.last_instruction
        last = EmittedInstruction(op_code=op_code, position=position)

        self.current_scope.previous_instruction = previous
        self.current_scope.last_instruction = last

    def _replace_instruction(
        self, position: int, new_instruction: code.Instructions
    ) -> None:
        self.current_scope.instructions[position : position + len(new_instruction)] = (
            new_instruction
        )
        op_code = new_instruction[0]
        self._set_last_instruction(code.OpCodes(bytes([op_code])), position)

    def _change_operand(self, position: int, operand: int) -> None:
        op_code = self.current_scope.instructions[position]
        op = code.OpCodes(bytes([op_code]))
        new_instruction = code.make(op, operand)
        self._replace_instruction(position, new_instruction)

    def _change_jump_location_after_consequence(self, position: int) -> None:
        after_consequence_position = len(self.current_scope.instructions)
        self._change_operand(position, after_consequence_position)

    def _last_instruction_is(self, op: code.OpCodes) -> bool:
        return bool(
            self.current_scope.last_instruction
            and self.current_scope.last_instruction.op_code == op
        )

    def _remove_pop(self) -> None:
        assert self.current_scope.last_instruction
        self.current_scope.instructions = code.Instructions(
            self.current_scope.instructions[
                : self.current_scope.last_instruction.position
            ]
        )
        self.current_scope.last_instruction = self.current_scope.previous_instruction

    def emit(self, op_code: code.OpCodes, *operands: int) -> int:
        instruction = code.make(op_code, *operands)
        position = self._add_instruction(instruction)

        self._set_last_instruction(op_code, position)
        return position

    def compile(self, node: ast.Node) -> None:
        try:
            match type(node):
                case ast.Program | ast.BlockStatement:
                    assert isinstance(node, ast.Program) or isinstance(
                        node, ast.BlockStatement
                    )
                    for statement in node.statements:
                        self.compile(statement)
                case ast.ExpressionStatement:
                    assert isinstance(node, ast.ExpressionStatement)
                    self.compile(node.expression)
                    self.emit(code.OpCodes.POP)
                case ast.Infix:
                    assert isinstance(node, ast.Infix) and node.right
                    if node.operator == "<":
                        self.compile(node.right)
                        self.compile(node.left)
                        self.emit(code.OpCodes.GREATER_THAN)
                        return

                    self.compile(node.left)
                    self.compile(node.right)

                    match node.operator:
                        case "+":
                            self.emit(code.OpCodes.ADD)
                        case "-":
                            self.emit(code.OpCodes.SUBTRACT)
                        case "/":
                            self.emit(code.OpCodes.DIVIDE)
                        case "*":
                            self.emit(code.OpCodes.MULTIPLY)
                        case ">":
                            self.emit(code.OpCodes.GREATER_THAN)
                        case "==":
                            self.emit(code.OpCodes.EQUAL)
                        case "!=":
                            self.emit(code.OpCodes.NOT_EQUAL)
                        case _:
                            raise NotImplementedError(node.operator)
                case ast.Prefix:
                    assert isinstance(node, ast.Prefix) and node.right
                    self.compile(node.right)

                    match node.operator:
                        case "!":
                            self.emit(code.OpCodes.EXCLAIMATION_MARK)
                        case "-":
                            self.emit(code.OpCodes.MINUS)
                        case _:
                            raise NotImplementedError
                case ast.IntegerLiteral:
                    assert isinstance(node, ast.IntegerLiteral)
                    integer = objects.Integer(value=node.value)
                    self.emit(code.OpCodes.CONSTANT, self._add_constant(integer))
                case ast.BooleanLiteral:
                    assert isinstance(node, ast.BooleanLiteral)
                    op_code = code.OpCodes.TRUE if node.value else code.OpCodes.FALSE
                    self.emit(op_code)
                case ast.If:
                    assert isinstance(node, ast.If)
                    self.compile(node.condition)

                    jump_position_non_truthy = self.emit(
                        code.OpCodes.JUMP_NOT_TRUTHY, FAKE_JUMP_VALUE
                    )

                    assert node.consequence
                    self.compile(node.consequence)

                    if self._last_instruction_is(code.OpCodes.POP):
                        self._remove_pop()

                    jump_position = self.emit(code.OpCodes.JUMP, FAKE_JUMP_VALUE)
                    self._change_jump_location_after_consequence(
                        jump_position_non_truthy
                    )

                    if node.alternative is None:
                        self.emit(code.OpCodes.NULL)
                    else:
                        self.compile(node.alternative)

                        if self._last_instruction_is(code.OpCodes.POP):
                            self._remove_pop()

                    self._change_jump_location_after_consequence(jump_position)
                case ast.Let:
                    assert isinstance(node, ast.Let)
                    self.compile(node.value)
                    symbol = self.symbol_table.define(node.name.value)
                    if symbol.scope is st.Scope.GLOBAL:
                        self.emit(code.OpCodes.SET_GLOBAL, symbol.index)
                    else:
                        self.emit(code.OpCodes.SET_LOCAL, symbol.index)
                case ast.Identifier:
                    assert isinstance(node, ast.Identifier)
                    try:
                        symbol = self.symbol_table.resolve(node.value)
                    except st.MissingDefinition:
                        # TODO - handle this
                        raise
                    self.load_symbol(symbol)
                case ast.StringLiteral:
                    assert isinstance(node, ast.StringLiteral)
                    string = objects.String(value=node.value)
                    self.emit(code.OpCodes.CONSTANT, self._add_constant(string))
                case ast.ArrayLiteral:
                    assert isinstance(node, ast.ArrayLiteral)

                    for item in node.items:
                        self.compile(item)
                    self.emit(code.OpCodes.ARRAY, len(node.items))
                case ast.Map:
                    assert isinstance(node, ast.Map)

                    keys: list[ast.Expression] = sorted(
                        list(node.pairs.keys()), key=lambda k: str(k)
                    )
                    for key in keys:
                        value = node.pairs[key]
                        self.compile(key)
                        self.compile(value)
                    self.emit(code.OpCodes.HASH, len(keys) * 2)
                case ast.Index:
                    assert isinstance(node, ast.Index)

                    self.compile(node.left)
                    self.compile(node.index)
                    self.emit(code.OpCodes.INDEX)
                case ast.FunctionLiteral:
                    assert isinstance(node, ast.FunctionLiteral)

                    self.enter_scope()

                    for param in node.parameters:
                        self.symbol_table.define(param.value)

                    if node.body:
                        self.compile(node.body)

                    if self._last_instruction_is(code.OpCodes.POP):
                        assert self.current_scope.last_instruction
                        self._replace_instruction(
                            self.current_scope.last_instruction.position,
                            code.make(code.OpCodes.RETURN_VALUE),
                        )
                    if not self._last_instruction_is(code.OpCodes.RETURN_VALUE):
                        self.emit(code.OpCodes.RETURN)

                    free_symbols = self.symbol_table.free_symbols
                    num_locals = self.symbol_table.num_definitions
                    func_scope_instructions = self.leave_scope()

                    for symbol in free_symbols:
                        self.load_symbol(symbol)

                    compiled_function = objects.CompiledFunction(
                        instructions=func_scope_instructions,
                        num_locals=num_locals,
                        num_params=len(node.parameters),
                    )
                    self.emit(
                        code.OpCodes.CLOSURE,
                        self._add_constant(compiled_function),
                        len(free_symbols),
                    )
                case ast.Return:
                    assert isinstance(node, ast.Return)
                    self.compile(node.value)
                    self.emit(code.OpCodes.RETURN_VALUE)
                case ast.Call:
                    assert isinstance(node, ast.Call)
                    self.compile(node.function)

                    for arg in node.arguments:
                        self.compile(arg)

                    self.emit(code.OpCodes.CALL, len(node.arguments))
                case _:
                    raise NotImplementedError(type(node))
        except Exception as exc:
            raise CouldntCompile(str(exc)) from exc

    def bytecode(self) -> Bytecode:
        return Bytecode(
            instructions=self.current_scope.instructions, constants=self.constants
        )
