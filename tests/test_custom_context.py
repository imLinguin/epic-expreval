from epic_expreval import Tokenizer, EvaluationContext

def test_math_functions():
    import math
    functions = {
        "pi": lambda c,i: math.pi
    }

    tk = Tokenizer("pi() * 3 < 10", EvaluationContext())
    tk.extend_functions(functions)
    tk.compile()
    assert tk.execute("")


def test_custom_state():
    # Create a class overwritig the EvaluationContext
    class CustomContext(EvaluationContext):
        def __init__(self):
            super().__init__()
            self.selection = set()

        def set_input(self, input: str):
            return super().set_input(input)


    # Define a function that interacts with the context
    def is_selected(context, input):
        return input in context.selection
    functions = {
        "IsSelected": is_selected 
    }

    # Provide custom context instance to tokenizer
    context = CustomContext()
    tk = Tokenizer("IsSelected(apple) && !IsSelected(banana)", context)
    # Provide our own functions and compile the expression
    tk.extend_functions(functions)
    tk.compile()

    # Update the state and run the expression against it
    context.selection.add("apple")
    assert tk.execute("")
    # Update again, and rerun the expression
    context.selection.add("banana")
    assert not tk.execute("")

