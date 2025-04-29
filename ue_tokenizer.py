from enum import Enum, auto
from typing import Any, Optional
import re

from evalctx import EvaluationContext
from functions import FUNCTION_DEFINITIONS
import logging


class TokenType(Enum):
    Function = 0
    Operator = auto()
    Scope = auto()
    Value = auto()

class Token:
    token_type: TokenType
    name: str
    param: Optional[Any]

    def __init__(self, t, n, p):
        self.token_type = t
        self.name = n
        self.param = None
        if len(p) > 0:
            self.param = p
            if p.isnumeric():
                self.param = int(p)

    def __str__(self):
        return f"{self.token_type} {self.name}" + ("(" + str(self.param) +")" if self.param is not None  else "")


operators = ["&&", "||", "==", "=", "+", "-", ">", "<", ">=", "<="]

end_bracket = re.compile(r"\)($|\s)")
def find_matching_bracket(index:int, input:str) -> int | None:
    find = end_bracket.search(input, index)
    return find and find.start()

def parse(input: str) -> list[Token]:
    logger = logging.getLogger("TOKENIZER")
    tokens = []
    token_type = None
    name_buf = ""
    value_buf = ""
    bracket_stack = 0
    
    i = 0
    
    while i < len(input):
        ch = input[i]
        if re.match(r"[a-zA-Z0-9&\|=+-<>]", ch):
            if token_type is None:
                token_type = TokenType.Value
                name_buf += ch
            elif token_type is TokenType.Function:
                value_buf += ch
            else:
                name_buf += ch
        elif ch.isspace():
            if name_buf in operators:
                token_type = TokenType.Operator
            if token_type is not None:
                tokens.append(Token(token_type, name_buf, value_buf))

            name_buf = ""
            value_buf = "" 
            token_type = None
        elif ch == '(':
            bracket_stack+=1
            if token_type == TokenType.Value:
                token_type = TokenType.Function
                logger.debug(f"Treating {name_buf} as function")
                # Find ending bracket if this is the function
                # Then load the param as is
                new_i = find_matching_bracket(i, input)
                if not new_i:
                     raise ValueError(f"Couldn't find a matching bracket for {i}")
                value_buf = input[i+1:new_i]
                i = new_i
            elif token_type == None:
                tokens.append(Token(TokenType.Scope, 'start', ''))
        elif ch == ')':
            bracket_stack-=1
            if token_type != TokenType.Function:
                if token_type is not None:
                    tokens.append(Token(token_type, name_buf, value_buf))
                tokens.append(Token(TokenType.Scope, 'end', ''))
                token_type = None
            if bracket_stack < 0:
                raise ValueError("Unmatched bracket")
        i += 1

    return tokens

def execute(tokens: list[Token], input: str) -> bool:
    logger = logging.getLogger("EVALUATOR")
    context = EvaluationContext(input)
    for token in tokens:
        logger.debug(token)
    for token in tokens:
        if token.token_type == TokenType.Function:
            func = FUNCTION_DEFINITIONS[token.name]
            res = func(context, token.param)
            context.add_op(res)
        elif token.token_type == TokenType.Scope:
            if token.name == "start":
                context.start_scope()
            else:
                context.end_scope()
        elif token.token_type == TokenType.Operator:
            context.add_op(token.name)
        elif token.token_type == TokenType.Value:
            context.add_op(token.name)
    return context.evaluation

