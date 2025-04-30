import re
import operator
from typing import Any, Callable, Optional
from dataclasses import dataclass


def and_func(a: Any, b: Any) -> bool:
    return a and b


def or_func(a: Any, b: Any) -> bool:
    return a or b


def not_func(a: Any, _b: Any) -> bool:
    return not a


OPERATOR_MAP = {
    "!": (20, "R", not_func),
    "NOT": (20, "R", not_func),
    "&&": (4, "L", and_func),
    "&": (4, "L", and_func),
    "AND": (4, "L", and_func),
    "||": (4, "L", or_func),
    "|": (4, "L", or_func),
    "OR": (4, "L", or_func),
    "=": (7, "L", operator.eq),
    ":": (7, "L", operator.eq),
    "==": (7, "L", operator.eq),
    "!=": (7, "L", operator.ne),
    "!:": (7, "L", operator.ne),
    ">": (8, "L", operator.gt),
    "<": (8, "L", operator.lt),
    "<=": (8, "L", operator.le),
    "<:": (8, "L", operator.le),
    ">=": (8, "L", operator.ge),
    ">:": (8, "L", operator.ge),
    "+": (15, "L", operator.add),
    "-": (15, "L", operator.sub),
    "*": (17, "L", operator.mul),
    "/": (17, "L", operator.truediv),
    "%": (17, "L", operator.mod),
    "^": (18, "L", operator.pow)
}


@dataclass
class Operation:
    left: Any = None
    op: Optional[Callable[[Any, Any], Any]] = None
    right: Any = None

    def eval(self) -> bool:
        if self.op is None:
            raise RuntimeError("Operator is None")
        if self.op == operator.eq and not self.left:
            return False
        return self.op(self.left, self.right)


class EvaluationContext:
    input: str
    regex_result: Optional[re.Match]

    def __init__(self):
        self.input = ""
        self.regex_result = None

    def set_input(self, input: str):
        self.input = input
        self.regex_result = None
                


