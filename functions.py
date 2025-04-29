import re
from typing import Any
from evalctx import EvaluationContext

def regex(context: EvaluationContext, param: str) -> bool:
    mx = re.compile(param)
    context.regex_result = mx.match(context.input)
    return bool(context.regex_result)

# Returns -1 in case of an error until we have proper short-circuting
def regex_group_int(context: EvaluationContext, param: str) -> int:
    return context.regex_result and int(context.regex_result.group(int(param))) or -1

def regex_group_string(context: EvaluationContext, param: str) -> str:
    return context.regex_result and context.regex_result.group(int(param)) or ""

FUNCTION_DEFINITIONS = {
    "Regex": regex,
    "RegexGroupInt64": regex_group_int,
    "RegexGroupString": regex_group_string
}
