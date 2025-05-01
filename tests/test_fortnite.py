from epic_expreval import Tokenizer, EvaluationContext

ctx = EvaluationContext()


def test_expr_true():
    tk = Tokenizer(
        "Regex(\\+\\+Fortnite\\+Release-(\\d+)\\.(\\d+).*-CL-(\\d+)-.*) && ((RegexGroupInt64(1) > 34 || (RegexGroupInt64(1) == 34 && RegexGroupInt64(2) >= 10)) && RegexGroupInt64(3) >= 39555844)",
        ctx,
    )
    tk.compile()
    assert tk.execute("++Fortnite+Release-34.40-CL-41753727-Windows")
    assert tk.execute("++Fortnite+Release-35.40-CL-41753727-Windows")
    assert tk.execute("++Fortnite+Release-35.05-CL-41753727-Windows")


def test_expr_falsy():
    tk = Tokenizer(
        "Regex(\\+\\+Fortnite\\+Release-(\\d+)\\.(\\d+).*-CL-(\\d+)-.*) && ((RegexGroupInt64(1) > 34 || (RegexGroupInt64(1) == 34 && RegexGroupInt64(2) >= 10)) && RegexGroupInt64(3) >= 39555844)",
        ctx,
    )
    tk.compile()
    assert not tk.execute("test123")
    assert not tk.execute("++Fortnite+Release-34.09-CL-41753727-Windows")
    assert not tk.execute("++Fortnite+Release-34.10-CL-39555843-Windows")
    assert not tk.execute("++Fortnite+Release-33.22-CL-41753727-Windows")
