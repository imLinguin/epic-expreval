from epic_expreval import Tokenizer, EvaluationContext


def test_asterisk():
    ctx = EvaluationContext()
    tx = Tokenizer("*", ctx)
    tx.compile()

    assert tx.execute("bad version")
    assert tx.execute("nice")
    assert tx.execute("v1.0.2")
    assert tx.execute("2.16.1")
