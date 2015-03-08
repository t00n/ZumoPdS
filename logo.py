"""
A minimalist LOGO interpreter written in Python by iTitou.

Example LOGO program

    pour carre :taille
        repete 4 [ av :taille dr 90 ]
    fin

    repete 10 [carre 10 dr 36]
"""

import math

# http://slps.github.io/zoo/logo/sdf.html

class Env(object):
    """An environment object, referencing its outer environment"""

    def __init__(self, parent=None, **content):
        self.parent = parent
        self.content = {k: v for k, v in content.iteritems()}

    def __getitem__(self, key):
        if key in self.content:
            return self.content[key]
        elif self.parent is not None:
            return self.parent[key]
        raise KeyError(key)

    def __setitem__(self, key, val):
        self.content[key] = val

    def __contains__(self, key):
        if key in self.content:
            return True
        elif self.parent:
            return key in self.parent
        return False

    @classmethod
    def lookup(klass, name):
        """Return a lambda(env) -> env[name]"""
        return lambda env: env[name]

class Callable(object):
    pass

class Procedure(Callable):
    """A user defined procedure, with named arguments"""

    def __init__(self, arg_names, body):
        self.arg_names = arg_names
        self.body = body

    @property
    def arity(self):
        return len(self.arg_names)

    def call(self, env, args):
        bound_args = dict(zip(self.arg_names, args))
        env = Env(parent=env, **bound_args)
        return self.body(env)

class Primitive(Callable):
    """A logo primitive, with unnamed arguments"""

    def __init__(self, func, arity=1):
        self.func = func
        self.arity = arity

    def call(self, env, args):
        return self.func(*args)

class ParseError(Exception):
    pass

def const(value):
    """Return a lambda(env) returning a constant value"""
    return lambda env: value

def sequentially(functions):
    """
    Return a lambda(env) executing functions sequentially, 
    returning the last one retval
    """
    if len(functions) > 0:
        return lambda env: map(lambda f: f(env), functions).pop()
    return lambda env: None

def repetition(times, func):
    """Return a lambda(env) executing a function multiple times"""
    def f(env):
        for i in range(times):
            func(env)
        return times
    return f

class Evaluator(object):
    def __init__(self, env=None):
        add = lambda a,b: a+b
        sub = lambda a,b: a-b
        mul = lambda a,b: a*b
        div = lambda a,b: a/b
        math_primitives = {
            "+": Primitive(add, 2),     "-": Primitive(sub, 2), 
            "*": Primitive(mul, 2),     "/": Primitive(div, 2),
            "sin": Primitive(math.sin), "cos": Primitive(math.cos),
        }
        self.env = Env(parent=env, **math_primitives)

    def analyze_repetition(self, tokens, i):
        times = int(tokens[i])
        if tokens[i+1] != "[":
            raise ParseError("Missing '['")
        i += 2

        funcs = []
        while tokens[i] != "]":
            f, i = self.analyze(tokens, i)
            funcs.append(f)
        
        return repetition(times, sequentially(funcs)), i+1

    def analyze_procedure(self, tokens, i):
        name = tokens[i]
        i += 1

        args = []
        while tokens[i][0] == ':':
            args.append(tokens[i])
            i += 1

        funcs = []
        while tokens[i] != "fin":
            f, i = self.analyze(tokens, i)
            funcs.append(f)

        body = sequentially(funcs)
        self.env[name] = Procedure(args, body)
        return None, i+1

    def analyze(self, tokens, i):
        """
        analyze(tokens, index) -> (lambda(env), next index)
        """
        res = None
        tok = tokens[i]
        i += 1

        if tok.isdigit():
            return const(int(tok)), i

        elif tok == '"':
            res = ""
            while tokens[i] != '"':
                res += " " + tokens[i]
                i += 1
            i += 1
            return const(res), i

        elif tok == "repete":
            return self.analyze_repetition(tokens, i)

        elif tok == "pour":
            return self.analyze_procedure(tokens, i)

        elif tok in self.env and isinstance(self.env[tok], Callable):
            proc = self.env[tok]
            args = []
            for argno in range(proc.arity):
                arg, i = self.analyze(tokens, i)
                args.append(arg)
            return lambda env: proc.call(env, map(lambda x: x(env), args)), i

        else:
            return Env.lookup(tok), i

    def eval(self, text):
        tokens = text.lower().replace('[', ' [ ').replace(']', ' ] ').replace('"', ' " ').split()
        i, prog = 0, []
        while i < len(tokens):
            func, i = self.analyze(tokens, i)
            if func is not None:
                prog.append(func)
        return sequentially(prog)(self.env)

if __name__ == "__main__":
    from sys import argv, stdin
    from zumoturtle import forward, backward, turnLeft, turnRight, setSpeed

    def wrap_print(text): 
        print text

    primitives_fr = {
        "ga": Primitive(turnLeft),  "gauche": Primitive(turnLeft),
        "dr": Primitive(turnRight), "droite": Primitive(turnRight),
        "av": Primitive(forward),   "avance": Primitive(forward),
        "re": Primitive(backward),  "recule": Primitive(backward),
        "vi": Primitive(setSpeed),  "vitesse": Primitive(setSpeed),
        "p": Primitive(wrap_print), "print": Primitive(wrap_print),
        "q": Primitive(exit, 0),
    }

    interpreter = Evaluator(env=Env(**primitives_fr))

    if len(argv) > 1:
        for script in argv[1:]:
            retval = interpreter.eval(open(script).read())
            print " =>", retval
    else:
        while True:
            try:
                retval = interpreter.eval(raw_input(" > "))
                print " => ", retval
            except KeyboardInterrupt:
                print
                continue
            except EOFError:
                print
                break

