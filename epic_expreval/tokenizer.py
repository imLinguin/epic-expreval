from enum import Enum, auto
from typing import Any, Callable
import re
import logging

from .evalctx import OPERATOR_MAP, EvaluationContext, Operation
from .functions import FUNCTION_DEFINITIONS


class TokenType(Enum):
    Function = 0
    Operator = auto()
    Scope = auto()
    Value = auto()

end_bracket = re.compile(r"\)($|\s)")


def find_matching_bracket(index: int, input: str) -> int | None:
    find = end_bracket.search(input, index)
    return find and find.start()


class Tokenizer:
    def __init__(self, exp: str, ctx: EvaluationContext):
        self.functions = FUNCTION_DEFINITIONS.copy()
        self.expression = exp
        self.wildcard = exp == "*"
        self.context = ctx
        self.tokens = self._parse()

    def extend_functions(
        self, new_functions: dict[str, Callable[[EvaluationContext, str], Any]]
    ):
        self.functions.update(new_functions)

    def overwrite_functions(
        self, new_functions: dict[str, Callable[[EvaluationContext, str], Any]]
    ):
        self.functions = new_functions

    def _parse(self) -> list[str]:
        output = []
        stack = []

        tokens = self._get_tokens()

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == "(":
                stack.append(token)
            elif token == ")":
                while stack and stack[-1] in OPERATOR_MAP and stack[-1] != "(":
                    output.append(stack.pop())
                if stack and stack[-1] == "(":
                    stack.pop()
                if stack and stack[-1] in self.functions:
                    output.append(stack.pop())
            elif token in self.functions:
                stack.append(token)
            elif token in OPERATOR_MAP:
                while (
                    stack
                    and stack[-1] in OPERATOR_MAP
                    and (
                        (OPERATOR_MAP[token][0] < OPERATOR_MAP[stack[-1]][0])
                        or (
                            OPERATOR_MAP[token][0] == OPERATOR_MAP[stack[-1]][0]
                            and OPERATOR_MAP[token][1] == "L"
                        )
                    )
                ):
                    output.append(stack.pop())
                stack.append(token)
            else:
                output.append(token)
            i += 1

        while stack:
            assert stack[-1] != "("
            output.append(stack.pop())
        
        return output

    def _get_tokens(self) -> list[str]:
        if self.wildcard:
            return []
        logger = logging.getLogger("TOKENIZER")
        tokens = []
        token_type = None
        name_buf = ""
        value_buf = ""
        bracket_stack = 0

        i = 0

        while i < len(self.expression):
            ch = self.expression[i]
            if re.match(r"[a-zA-Z0-9&\|=\+\-<>\^\*!\/\%]", ch):
                if ch in ["+", "-", "^", "*", "/", "%", "!"]:
                    if name_buf:
                        tokens.append(name_buf)
                        name_buf = ""
                    tokens.append(ch)
                elif token_type is None:
                    token_type = TokenType.Value
                    name_buf += ch
                else:
                    name_buf += ch
            elif ch.isspace():
                if name_buf:
                    tokens.append(name_buf)
                name_buf = ""
                value_buf = ""
                token_type = None
            elif ch == "(":
                bracket_stack += 1
                if token_type == TokenType.Value:
                    token_type = None
                    logger.debug(f"Treating {name_buf} as function")
                    # Find ending bracket if this is the function
                    # Then load the param as is
                    new_i = find_matching_bracket(i, self.expression)
                    if not new_i:
                        raise ValueError(f"Couldn't find a matching bracket for {i}")
                    tokens.append(name_buf)
                    tokens.append("(")
                    if new_i == i + 1:
                        value_buf = ""
                    else:
                        value_buf = self.expression[i + 1 : new_i]
                        i = new_i - 1
                    if value_buf:
                        tokens.append(value_buf)
                    value_buf = ""
                    name_buf = ""

                elif token_type == None:
                    tokens.append(ch)
            elif ch == ")":
                bracket_stack -= 1
                if name_buf:
                    tokens.append(name_buf)
                    name_buf = ""
                tokens.append(ch)
                token_type = None
                if bracket_stack < 0:
                    raise ValueError("Unmatched bracket")
            i += 1
        if name_buf:
            tokens.append(name_buf)

        if bracket_stack != 0:
            raise ValueError("Unmatched bracket")

        return tokens

    def execute(self, input: str) -> bool:
        if self.wildcard:
            return True
        logger = logging.getLogger("EVALUATOR")
        self.context.set_input(input)

        for token in self.tokens:
            logger.debug(token)

        exec_stack = []
        for token in self.tokens:
            if token in self.functions:
                arg = None
                if exec_stack:
                    arg = exec_stack[-1]
                if arg and arg not in OPERATOR_MAP:
                    arg = exec_stack.pop()

                func = self.functions[token]
                res = func(self.context, str(arg or ""))
                exec_stack.append(res)
            elif token in OPERATOR_MAP:
                if OPERATOR_MAP[token][1] == 'L':
                    b = exec_stack.pop()
                    if type(b) == str and b.isnumeric():
                        b = int(b)
                    a = exec_stack.pop()
                    if type(a) == str and a.isnumeric():
                        a = int(a)
                    exec_stack.append(Operation(a, OPERATOR_MAP[token][2], b).eval())
                else:
                    a = exec_stack.pop()
                    if type(a) == str and a.isnumeric():
                        a = int(a)
                    exec_stack.append(Operation(bool(a), OPERATOR_MAP[token][2], None).eval())
            else:
                exec_stack.append(token)

        return exec_stack[0] 
