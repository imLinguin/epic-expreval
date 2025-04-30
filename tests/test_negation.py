from epic_expreval import Tokenizer, EvaluationContext

def test_not():
    assert Tokenizer("NOT (2 > 3)", EvaluationContext()).execute("")
    assert Tokenizer("!(2 > 3)", EvaluationContext()).execute("")
