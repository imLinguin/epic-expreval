from epic_expreval import Tokenizer, EvaluationContext


def test_asterisk():
    ctx = EvaluationContext()
    tx = Tokenizer("*", ctx)

    assert tx.execute("bad version")
    assert tx.execute("nice")
    assert tx.execute("v1.0.2")
