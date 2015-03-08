from logo import Evaluator

def logo_eval(text):
    return Evaluator().eval(text)

def test_eval_const_int():
    assert logo_eval("3") == 3

def test_eval_const_str():
    assert logo_eval('"This is a string"') == "This is a string"

def test_eval_add():
    assert logo_eval("+ 3 4") == 7

def test_eval_sub():
    assert logo_eval("- 3 4") == -1

def test_eval_mul():
    assert logo_eval("* 3 4") == 12

def test_eval_div():
    assert logo_eval("/ 3 4") == 0

def test_eval_proc():
    assert logo_eval("pour add1 :n + 1 :n fin add1 3") == 4
