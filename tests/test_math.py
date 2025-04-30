from epic_expreval import Tokenizer, EvaluationContext

def test_addition():
    tk = Tokenizer("13 + 51", EvaluationContext())
    tk.compile()
    assert tk.execute("") == 13 + 51
    
def test_subtraction():
    tk = Tokenizer("51 - 51", EvaluationContext())
    tk.compile()
    assert tk.execute("") == 0

def test_delta():
    tk = Tokenizer("5^2 + 2*5 + 1", EvaluationContext())
    tk.compile()
    assert tk.execute("") == 36 

def test_exec_order():
    tk = Tokenizer("3+3*3", EvaluationContext())
    tk.compile()
    assert tk.execute("") == 12
    tk = Tokenizer("15-3^2", EvaluationContext())
    tk.compile()
    assert tk.execute("") == 6
    tk = Tokenizer("(2+4)^2", EvaluationContext())
    tk.compile()
    assert tk.execute("") == 36

