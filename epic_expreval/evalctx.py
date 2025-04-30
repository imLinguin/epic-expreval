import re
import operator
from typing import Any, Callable, Optional
from dataclasses import dataclass

def and_func(a: Any, b: Any) -> bool:
    return a and b

def or_func(a: Any, b: Any) -> bool:
    return a or b

OPERATOR_MAP = {
    "&&": and_func,
    "&": and_func,
    "AND": and_func,
    "||": or_func,
    "|": or_func,
    "OR": or_func,
    "=": operator.eq,
    ":": operator.eq,
    "==": operator.eq,
    "!=": operator.ne,
    "!:": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    "<=": operator.le,
    "<:": operator.le,
    ">=": operator.ge,
    ">:": operator.ge,
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

    scope_data: list[Operation]

    def __init__(self):
        self.input = ""
        self.regex_result = None
        
        self.scope_data = [Operation()]

    @property
    def evaluation(self):
        return self.scope_data[0].eval()
        
    def add_op(self, res: Any):
        op = self.scope_data[-1]
        if type(res) == str:
            if res.isnumeric():
                res = int(res)
        if op.left is None:
            op.left = res
        elif op.op is None:
            op.op = OPERATOR_MAP[res]
        elif op.right is None:
            op.right = res
        elif res in OPERATOR_MAP:
            # Handle inline expressions
            # (that are not scoped with brackets)
            op.left = op.eval()
            op.op = OPERATOR_MAP[res]
            op.right = None

    def start_scope(self):
        self.scope_data.append(Operation())
    def end_scope(self):
        op = self.scope_data.pop()
        if op:
            self.add_op(op.eval())
