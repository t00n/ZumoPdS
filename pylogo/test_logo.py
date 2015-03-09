from logo import Evaluator, Env, Primitive

def logo_eval(text, **env):
    return Evaluator(Env(parent=None, **env)).eval(text)

class Counter:
    def __init__(self):
        self.calls = 0

    def f(self):
        print "Call", repr(self)
        self.calls += 1
        return self.calls

    def primitive(self):
        return Primitive(self.f, 0)

def test_eval_const_int():
    assert logo_eval("3") == 3

def test_eval_const_str():
    assert logo_eval('"This is a string"') == "This is a string"

def test_eval_const_list():
    assert logo_eval("[1 2 3]") == [1, 2, 3]

def test_eval_add():
    assert logo_eval("+ 3 4") == 7
    assert logo_eval("+ [3 4] [5 6]") == [3, 4, 5, 6]

def test_eval_sub():
    assert logo_eval("- 3 4") == -1

def test_eval_mul():
    assert logo_eval("* 3 4") == 12

def test_eval_div():
    assert logo_eval("/ 3 4") == 0

def test_eval_if():
    assert logo_eval("si 3 4 sinon 5") == 4
    assert logo_eval("si 0 4 sinon 5") == 5

def test_eval_cmp():
    assert logo_eval('si < 3 4 "oui" sinon "non"') == "oui"
    assert logo_eval('si < 4 4 "oui" sinon "non"') == "non"

    assert logo_eval('si <= 4 4 "oui" sinon "non"') == "oui"
    assert logo_eval('si <= 5 4 "oui" sinon "non"') == "non"

    assert logo_eval('si = 4 4 "oui" sinon "non"') == "oui"
    assert logo_eval('si = 5 4 "oui" sinon "non"') == "non"

    assert logo_eval('si >= 4 4 "oui" sinon "non"') == "oui"
    assert logo_eval('si >= 3 4 "oui" sinon "non"') == "non"

    assert logo_eval('si > 5 4 "oui" sinon "non"') == "oui"
    assert logo_eval('si > 4 4 "oui" sinon "non"') == "non"

def test_eval_proc():
    assert logo_eval("pour add1 :n + 1 :n fin add1 3") == 4

def test_eval_my_primitive():
    assert logo_eval("f 41", f=Primitive(lambda n: n + 1)) == 42

def test_eval_closure():
    source = """
    pour addition :a :b
      pour add :n 
        + :a :n 
      fin
      add :b
    fin
    addition 16 26
    """
    assert logo_eval(source) == 42

def test_counter():
    c = Counter()
    logo_eval('func', func=c.primitive())
    assert c.calls == 1

def test_loop():
    c = Counter()
    assert logo_eval("repete 10 [func]", func=c.primitive()) == 10
    assert c.calls == 10
