from enum import Enum, auto
from typing import Any, Callable, Optional
import re
import logging

from .evalctx import OPERATOR_MAP, EvaluationContext, Operation, FunctionCall, AST
from .functions import FUNCTION_DEFINITIONS


class TokenType(Enum):
    Function = 0
    Operator = auto()
    Scope = auto()
    Value = auto()


end_bracket = re.compile(r"\)($|\s)")


def find_matching_bracket(index: int, input: str) -> Optional[int]:
    find = end_bracket.search(input, index)
    return find and find.start()


class Tokenizer:
    def __init__(self, exp: str, ctx: EvaluationContext):
        self.functions = FUNCTION_DEFINITIONS.copy()
        self.expression = exp
        self.wildcard = exp == "*"
        self.context = ctx
        self.tree = []

    def extend_functions(
        self, new_functions: dict[str, Callable[[EvaluationContext, str], Any]]
    ):
        self.functions.update(new_functions)

    def overwrite_functions(
        self, new_functions: dict[str, Callable[[EvaluationContext, str], Any]]
    ):
        self.functions = new_functions

    def compile(self):
        self.tree = self._parse()

    def _parse(self) -> AST:
        parse_stack = []

        tokens = self._get_tokens()

        scopes: list[tuple[AST, AST]] = [(None, None)]
        i = 0
       
        while i < len(tokens):
            token = tokens[i]
            node, current_node = scopes[-1]
            new_node: AST = None
            if token in self.functions:
                ntoken = tokens[i+2] if tokens[i+2] not in "()" else None
                new_node = FunctionCall(self.functions[token], ntoken)
                i += 3 if ntoken else 2
            elif token == "(":
                scopes.append((None, None))
                node = None
                current_node = None
            elif token == ")":
                n, cn = scopes.pop()
                node, current_node = scopes[-1]
                if node is None:
                    n.scoped = True
                    node = n
                    current_node = n
                else:
                    current_node.attach_node(n, True)
            elif token in OPERATOR_MAP:
                new_node = Operation(token)
                if parse_stack:
                    new_node.attach_node(parse_stack.pop())
            else:
                if isinstance(current_node, Operation):
                    current_node.attach_node(token)
                else:
                    parse_stack.append(token)
                
            if new_node:
                if node is None:
                    node = new_node
                    current_node = node
                elif isinstance(current_node, Operation):
                    current_node = current_node.attach_node(new_node)
                elif isinstance(node, FunctionCall):
                    new_node.attach_node(node)
                    node = new_node
                    current_node = new_node

            i += 1
            scopes[-1] = (node, current_node)

        if parse_stack:
            scopes[0][1].attach_node(parse_stack.pop())
        return scopes[0][0]

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

    def execute(self, input: str) -> Any:
        if self.wildcard:
            return True
        self.context.set_input(input)
        return self.tree.eval(self.context)

