import re
import operator
from typing import Any, Callable, Optional
from dataclasses import dataclass
import logging


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
    "^": (18, "L", operator.pow),
}

class EvaluationContext:
    input: str
    regex_result: Optional[re.Match]

    def __init__(self):
        self.input = ""
        self.regex_result = None

    def reset(self):
        self.regex_result = None
        
    def set_input(self, input: str):
        self.input = input
        self.regex_result = None

class AST:
    def eval(self, context: EvaluationContext) -> Any:
        pass

@dataclass
class Operation(AST):
    op: str
    left: Any = None
    right: Any = None

    def eval(self, context):
        operator = OPERATOR_MAP[self.op]
        func = operator[2]
        
        if isinstance(self.left, AST):
            lvalue = self.left.eval(context)
        else:
            lvalue = self.left
        
        if func == and_func and not bool(lvalue):
            return False
        if func == or_func and bool(lvalue):
            return True

        if isinstance(self.right, AST):
            rvalue = self.right.eval(context)
        else:
            rvalue = self.right
        if str(lvalue).isdecimal():
            lvalue = int(lvalue)
        if str(rvalue).isdecimal():
            rvalue = int(rvalue)
        logging.getLogger("OPERATION").debug("%s(%s,%s)", self.op, lvalue, rvalue)
        return func(lvalue, rvalue)

    def replace(self, node):
        copy = Operation(self.op, self.left, self.right)
        self.op = node.op
        self.left = node.left
        self.right = node.right
        
        node.op = copy.op
        node.left = copy.left
        node.right = copy.right

    def attach_node(self, node, skip_replace=False) -> AST:
        replaced = False
        if isinstance(node, Operation) and not skip_replace:
            self_level = OPERATOR_MAP[self.op][0]
            node_level = OPERATOR_MAP[node.op][0]
            if node_level < self_level:
                self.replace(node)
                replaced = True

        if self.left is None:
            self.left = node
        elif self.right is None:
            self.right = node
        elif self.right is not None:
            # This assumes node.right is not set
            node.right = node.left
            node.left = self.right
            self.right = node
        if isinstance(node, FunctionCall):
            return self
        return self if replaced else node

@dataclass
class FunctionCall(AST):
    function: Callable[[EvaluationContext, str], Any]
    param: str    

    def eval(self, context):
        logging.getLogger("FUNCTIONCALL").debug("eval of %s %s", self.function, self.param)
        return self.function(context, self.param)