from epic_expreval import Tokenizer, EvaluationContext


def test_not():
    tk = Tokenizer("NOT (2 > 3)", EvaluationContext())
    tk.compile()
    assert tk.execute("")
    Tokenizer("!(2 > 3)", EvaluationContext())
    tk.compile()
    assert tk.execute("")
