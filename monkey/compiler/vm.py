from __future__ import annotations
from typing import TYPE_CHECKING, cast

import dataclasses as dc

from monkey.interpreter import objects
from monkey.compiler import code, compilers, frames

if TYPE_CHECKING:
    from typing import Final

    from monkey.compiler import compilers


STACK_SIZE: Final = 2048
GLOBALS_SIZE: Final = 65536
MAX_FRAMES: Final = 1024

TRUE = objects.Boolean(value=True)
FALSE = objects.Boolean(value=False)
NULL = objects.Null()


class VMError(Exception):
    pass


class Unhandled(VMError):
    pass


class BadIndex(VMError):
    pass


class StackError(VMError):
    pass


class MismatchedNumberOfParams(VMError):
    pass


class Missing(StackError):
    pass


class Empty(StackError):
    pass


class Overflow(StackError):
    pass


def is_truthy(obj: objects.Object) -> bool:
    if isinstance(obj, objects.Boolean):
        return obj.value
    return True


@dc.dataclass
class VM:
    stack_pointer: int
    stack: list[objects.Object | None]

    globals: list[objects.Object | None]

    constants: list[objects.Object]

    frames: list[frames.Frame | None]
    frames_index: int

    @classmethod
    def from_bytecode(
        cls,
        bytecode: compilers.Bytecode,
        state: list[objects.Object | None] | None = None,
    ) -> VM:
        main_func = objects.CompiledFunction(
            instructions=bytecode.instructions,
            num_locals=0,
            num_params=0,
        )
        main_frame = frames.Frame.new(
            objects.Closure(function=main_func, free=[]),
            0,
        )
        frames_: list[frames.Frame | None] = [None] * MAX_FRAMES
        frames_[0] = main_frame

        return cls(
            globals=state or ([None] * GLOBALS_SIZE),
            constants=bytecode.constants,
            stack_pointer=0,
            stack=[None] * STACK_SIZE,
            frames=frames_,
            frames_index=1,
        )

    def current_frame(self) -> frames.Frame:
        try:
            if frame := self.frames[self.frames_index - 1]:
                return frame
        except IndexError:
            pass

        raise Missing

    def pop_frame(self) -> frames.Frame:
        if self.frames_index < 0:
            raise Missing

        if f := self.frames[self.frames_index - 1]:
            self.frames[self.frames_index - 1] = None
            self.frames_index -= 1
            return f

        raise Missing

    def run(self) -> None:
        instructions: code.Instructions
        op_code: code.OpCodes

        while self.current_frame().instruction_pointer < (
            len(self.current_frame().instructions) - 1
        ):
            self.current_frame().instruction_pointer += 1

            instructions = self.current_frame().instructions
            op_code = code.OpCodes(
                bytes([instructions[self.current_frame().instruction_pointer]])
            )

            match op_code:
                case code.OpCodes.CONSTANT:
                    const_index = code.read_int16(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 2

                    to_add = self.constants[const_index]
                    self.push(to_add)
                case (
                    code.OpCodes.ADD
                    | code.OpCodes.SUBTRACT
                    | code.OpCodes.MULTIPLY
                    | code.OpCodes.DIVIDE
                ):
                    self.execute_binary_operation(op_code)
                case code.OpCodes.POP:
                    self.pop()
                case code.OpCodes.TRUE | code.OpCodes.FALSE:
                    self.push(TRUE if op_code == code.OpCodes.TRUE else FALSE)
                case (
                    code.OpCodes.GREATER_THAN
                    | code.OpCodes.EQUAL
                    | code.OpCodes.NOT_EQUAL
                ):
                    self.execute_comparison(op_code)
                case code.OpCodes.MINUS | code.OpCodes.EXCLAIMATION_MARK:
                    self.execute_operator(op_code)
                case code.OpCodes.JUMP:
                    position = code.read_int16(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer = position - 1
                case code.OpCodes.JUMP_NOT_TRUTHY:
                    position = code.read_int16(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 2

                    cond = self.pop()
                    if not is_truthy(cond):
                        self.current_frame().instruction_pointer = position - 1
                case code.OpCodes.NULL:
                    self.push(NULL)
                case code.OpCodes.SET_GLOBAL:
                    global_index = code.read_int16(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 2
                    self.globals[global_index] = self.pop()
                case code.OpCodes.GET_GLOBAL:
                    global_index = code.read_int16(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 2

                    obj = self.globals[global_index]
                    assert obj
                    self.push(obj)
                case code.OpCodes.ARRAY:
                    num_elements = code.read_int16(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 2

                    start = self.stack_pointer - num_elements
                    array = self.build_array(start, self.stack_pointer)
                    self.stack_pointer -= num_elements
                    self.push(array)
                case code.OpCodes.HASH:
                    num_elements = code.read_int16(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 2

                    start = self.stack_pointer - num_elements
                    map = self.build_hash_map(start, self.stack_pointer)
                    self.push(map)
                case code.OpCodes.INDEX:
                    index = self.pop()
                    left = self.pop()
                    self.execute_index_operation(left, index)
                case code.OpCodes.GET_BUILTIN:
                    builtin_index = code.read_int8(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 1

                    definition = objects.BUILTINS[builtin_index]
                    self.push(definition)
                case code.OpCodes.CALL:
                    num_args = code.read_int8(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 1
                    self.execute_call(num_args)
                case code.OpCodes.RETURN_VALUE:
                    value = self.pop()

                    frame = self.pop_frame()
                    self.stack_pointer = frame.base_pointer
                    self.pop()

                    self.push(value)
                case code.OpCodes.RETURN:
                    frame = self.pop_frame()
                    self.stack_pointer = frame.base_pointer

                    self.pop()

                    self.push(NULL)
                case code.OpCodes.SET_LOCAL:
                    local_index = code.read_int8(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 1

                    frame = self.current_frame()
                    self.stack[frame.base_pointer + local_index] = self.pop()
                case code.OpCodes.GET_LOCAL:
                    local_index = code.read_int8(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    self.current_frame().instruction_pointer += 1

                    frame = self.current_frame()
                    obj = self.stack[frame.base_pointer + local_index]
                    assert obj
                    self.push(obj)
                case code.OpCodes.CLOSURE:
                    const_index = code.read_int16(
                        instructions, self.current_frame().instruction_pointer + 1
                    )
                    _ = code.read_int8(
                        instructions, self.current_frame().instruction_pointer + 3
                    )
                    self.current_frame().instruction_pointer += 3

                    self.push_closure(const_index)
                case _:
                    raise NotImplementedError(op_code)

    @property
    def last_popped_stack_elem(self) -> objects.Object:
        if item := self.stack[self.stack_pointer]:
            return item
        raise Empty

    def push(self, o: objects.Object) -> None:
        if self.stack_pointer >= STACK_SIZE:
            raise Overflow

        self.stack[self.stack_pointer] = o
        self.stack_pointer += 1

    def push_frame(self, frame: frames.Frame) -> None:
        self.frames[self.frames_index] = frame
        self.frames_index += 1

    def push_closure(self, closure_index: int) -> None:
        func = self.constants[closure_index]
        assert isinstance(func, objects.CompiledFunction)

        closure = objects.Closure(function=func, free=[])
        return self.push(closure)

    def pop(self) -> objects.Object:
        if self.stack_pointer <= 0:
            raise Empty

        o = self.stack[self.stack_pointer - 1]
        if o is None:
            raise Missing(f"No value at {self.stack_pointer - 1}")

        self.stack_pointer -= 1
        return o

    def build_hash_map(self, start: int, end: int) -> objects.Hash:
        map: dict[objects.HashKey, objects.HashPair] = {}

        for i in range(start, end, 2):
            key = self.stack[i]
            value = self.stack[i + 1]

            assert key and value, f"Key: {key}, Value: {value}"
            assert isinstance(key, objects.Hashable)

            pair = objects.HashPair(key, value)
            map[key.hash_key()] = pair

        return objects.Hash(map)

    def build_array(self, start: int, end: int) -> objects.Array:
        elements: list[objects.Object | None] = [None] * (end - start)

        for i in range(start, end):
            elements[i - start] = self.stack[i]

        assert None not in elements
        return objects.Array(items=cast(list[objects.Object], elements))

    # Operations
    def execute_call(self, num_args: int) -> None:
        function_or_closure = self.stack[self.stack_pointer - 1 - num_args]
        match type(function_or_closure):
            case objects.Closure:
                assert isinstance(function_or_closure, objects.Closure)
                return self.call_compiled_function(function_or_closure, num_args)
            case objects.BuiltInFunction:
                assert isinstance(function_or_closure, objects.BuiltInFunction)
                return self.call_builtin_function(function_or_closure, num_args)
            case _:
                raise Unhandled(
                    f"Can't call function of type: '{type(function_or_closure)}'"
                )

    def call_compiled_function(self, closure: objects.Closure, num_args: int) -> None:
        if closure.function.num_params != num_args:
            raise MismatchedNumberOfParams(
                f"Expected {closure.function.num_params}, got {num_args}"
            )

        frame = frames.Frame.new(closure, self.stack_pointer - num_args)
        self.push_frame(frame)
        self.stack_pointer = frame.base_pointer + closure.function.num_locals

    def call_builtin_function(
        self, func: objects.BuiltInFunction, num_args: int
    ) -> None:
        args = self.stack[self.stack_pointer - num_args : self.stack_pointer]
        assert all(args)

        result = func.function(*[arg for arg in args if arg is not None])
        self.stack_pointer = self.stack_pointer - num_args - 1

        if result:
            self.push(result)
        else:
            self.push(NULL)

    def execute_binary_operation(self, op: code.OpCodes) -> None:
        right = self.pop()
        left = self.pop()

        if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
            return self.execute_binary_integer_operation(op, left, right)
        elif isinstance(left, objects.String) and isinstance(right, objects.String):
            return self.execute_binary_string_operation(op, left, right)
        raise NotImplementedError(op, left, right)

    def execute_binary_integer_operation(
        self, op: code.OpCodes, left: objects.Integer, right: objects.Integer
    ) -> None:
        match op:
            case code.OpCodes.ADD:
                result = left.value + right.value
            case code.OpCodes.MULTIPLY:
                result = left.value * right.value
            case code.OpCodes.SUBTRACT:
                result = left.value - right.value
            case code.OpCodes.DIVIDE:
                result = left.value // right.value
            case _:
                raise Unhandled(op)
        self.push(objects.Integer(value=result))

    def execute_operator(self, op: code.OpCodes) -> None:
        match op:
            case code.OpCodes.MINUS:
                return self.execute_minus_operator()
            case code.OpCodes.EXCLAIMATION_MARK:
                return self.execute_exclaimation_mark_operator()
            case _:
                raise Unhandled(f"Not a valid prefix operator: {str(op)}")

    def execute_exclaimation_mark_operator(self) -> None:
        operand = self.pop()

        if operand is TRUE:
            self.push(FALSE)
        elif operand is FALSE:
            self.push(TRUE)
        elif operand is NULL:
            self.push(TRUE)
        else:
            self.push(FALSE)

    def execute_minus_operator(self) -> None:
        operand = self.pop()

        if not isinstance(operand, objects.Integer):
            raise Unhandled(operand)

        self.push(objects.Integer(value=operand.value * -1))

    def execute_comparison(self, op: code.OpCodes) -> None:
        right = self.pop()
        left = self.pop()

        if isinstance(left, objects.Integer) and isinstance(right, objects.Integer):
            return self.execute_integer_comparison(op, left, right)
        if isinstance(left, objects.Boolean) and isinstance(right, objects.Boolean):
            return self.execute_boolean_comparison(op, left, right)

        raise Unhandled(f"{op} between {type(left)} and {type(right)}")

    def execute_integer_comparison(
        self, op: code.OpCodes, left: objects.Integer, right: objects.Integer
    ) -> None:
        result: bool
        match op:
            case code.OpCodes.EQUAL:
                result = left.value == right.value
            case code.OpCodes.GREATER_THAN:
                result = left.value > right.value
            case code.OpCodes.NOT_EQUAL:
                result = left.value != right.value
            case _:
                raise Unhandled(f"{op} not handled for integer comparisons.")
        self.push(objects.Boolean(value=result))

    def execute_binary_string_operation(
        self, op: code.OpCodes, left: objects.String, right: objects.String
    ) -> None:
        result: str

        match op:
            case code.OpCodes.ADD:
                result = left.value + right.value
            case _:
                raise Unhandled(op)

        self.push(objects.String(value=result))

    def execute_boolean_comparison(
        self, op: code.OpCodes, left: objects.Boolean, right: objects.Boolean
    ) -> None:
        result: bool
        left = TRUE if left.value else FALSE
        right = TRUE if right.value else FALSE

        match op:
            case code.OpCodes.EQUAL:
                result = left is right
            case code.OpCodes.NOT_EQUAL:
                result = left is not right
            case _:
                raise Unhandled(f"{op} not handled for boolean comparisons.")
        self.push(TRUE if result else FALSE)

    def execute_index_operation(
        self, left: objects.Object, index: objects.Object
    ) -> None:
        if isinstance(left, objects.Array) and isinstance(index, objects.Integer):
            return self.execute_array_index(left, index)
        if isinstance(left, objects.Hash) and isinstance(index, objects.Hashable):
            return self.execute_hash_map_index(left, index)

        raise Unhandled(f"Indexing not on {type(left)} with {type(index)}")

    def execute_array_index(self, array: objects.Array, index: objects.Integer) -> None:
        num_objects = len(array.items)
        if index.value > num_objects or index.value < 0:
            raise BadIndex(f"{index.value} on {type(array)} ({num_objects} objects)")
        try:
            self.push(array.items[index.value])
        except IndexError as exc:
            raise Missing from exc

    def execute_hash_map_index(
        self, map: objects.Hash, index: objects.Hashable
    ) -> None:
        key = index.hash_key()
        try:
            self.push(map.pairs[key].value)
        except KeyError as exc:
            raise Missing from exc
