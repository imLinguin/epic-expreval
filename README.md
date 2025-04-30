# epic-expreval

Epic expression evaluator

## Usage

Basic usage is quite simple.
At the moment the library provides following functions that can be used in expressions

- Regex
- RegexGroupInt64
- RegexGroupString
- RandomAccessMemoryGB

```python
from epic_expreval import Tokenizer, EvaluationContext

# Initialize tokenizer with expression and context
ctx = EvaluationContext()
tk = Tokenizer("<expression here>", ctx)
# Parse the expression, call this after you are done setting the Tokenizer up
tk.compile()

# Run the expression against the input
tk.execute("<input here>")
```

## Adding more functions

At least in Selective Downloads manifests, Epic uses more functions that are related to DirectX, UI state or even game ownership.
For obvious reasons those functions can't be implemented by this library out of the box.

However extending available functions is also really simple

```python

from epic_expreval import Tokenizer, EvaluationContext

def my_function(context: EvaluationContext, param: str):
    # Do your stuff here, you are also free to extend EvaluationContext to add your own fields
    return True 

new_functions = {
    "MyFunction": my_function
}

# Initialize tokenizer with expression and context
ctx = EvaluationContext()
tk = Tokenizer("MyFunction()", ctx)
# This will call an update on dict
# So this can also be used to overwrite functions provided by this library
tk.extend_functions(new_functions)
# You can also completely nuke built-in functions
# tk.overwrite_functions(new_functions)

# Parse the expression
tk.compile()
# Parse and run the expression against the input
tk.execute("<input here>")
```


## Remarks

At the moment the library doesn't handle short-circuting in AND (&&) statements

