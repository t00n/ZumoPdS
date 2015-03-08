"""
A minimalist LOGO interpreter written in Python by iTitou.

Example LOGO program

    pour carre :taille
        repete 4 [ av :taille dr 90 ]
    fin

    repete 10 [carre 10 dr 36]
"""

# http://slps.github.io/zoo/logo/sdf.html

from zumoturtle import forward, backward, turnLeft, turnRight, setSpeed

class Env(object):
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

class Callable(object):
    pass

class Procedure(Callable):
    """A user defined procedure, with named arguments"""

    def __init__(self, args, body):
        self.args = args
        self.body = body

    @property
    def arity(self):
        return len(self.args)

    def call(self, env, args):
        bound_args = dict(zip(self.args, args))
        env = Env(parent=env, **bound_args)
        return self.body(env)

class Primitive(Callable):
    """A logo primitive, with unnamed arguments"""

    def __init__(self, func, arity):
        self.func = func
        self.arity = arity

    def call(self, env, args):
        self.func(*args)

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
    return lambda env: map(lambda f: f(env), functions).pop()

def repetition(times, func):
    """Return a lambda(env) executing a function multiple times"""
    def f(env):
        for i in range(times):
            func(env)
        return times
    return f

def env_lookup(name):
    """Return a lambda(env) that returns the value associated to name in env"""
    return lambda env: env[name]

def logo_analyze_repetition(tokens, procedures):
    times = int(tokens[0])
    if tokens[1] != "[":
        raise ParseError("Missing '['")
    tokens = tokens[2:]
    funcs = []
    while tokens[0] != "]":
        f, tokens = logo_analyze(tokens, procedures)
        funcs.append(f)
    tokens = tokens[1:]
    return repetition(times, sequentially(funcs)), tokens

def logo_analyze_procedure(tokens, procedures):
    name = tokens[0]
    args = []

    i = 1
    while tokens[i][0] == ':':
        args.append(tokens[i])
        i += 1
    tokens = tokens[i:]

    funcs = []
    while tokens[0] != "fin":
        f, tokens = logo_analyze(tokens, procedures)
        funcs.append(f)
    tokens = tokens[1:]

    body = sequentially(funcs)
    procedures[name] = Procedure(args, body)
    return None, tokens

def logo_analyze_call(proc_name, tokens, procedures):
    proc = procedures[proc_name]
    args = []
    for i in range(proc.arity):
        arg, tokens = logo_analyze(tokens, procedures)
        args.append(arg)
    return lambda env: proc.call(env, map(lambda x: x(env), args)), tokens

def logo_analyze(tokens, procedures):
    """
    analyze(tokens, procedures) -> (lambda(env), remaining tokens)
    """
    res = None
    tok, tokens = tokens[0], tokens[1:]

    if tok.isdigit():
        return const(int(tok)), tokens

    elif tok == "repete":
        return logo_analyze_repetition(tokens, procedures)

    elif tok == "pour":
        return logo_analyze_procedure(tokens, procedures)

    elif tok in procedures:
        return logo_analyze_call(tok, tokens, procedures)

    else:
        return env_lookup(tok), tokens

def logo_eval(text):
    tokens = text.lower().replace('[', ' [ ').replace(']', ' ] ').split()
    env = Env(
        ga=Primitive(turnLeft, 1), 
        dr=Primitive(turnRight, 1), 
        av=Primitive(forward, 1), 
        re=Primitive(backward, 1), 
        vi=Primitive(setSpeed, 1)
    )

    try:
        prog = []
        while len(tokens) > 0:
            func, tokens = logo_analyze(tokens, env)
            if func is not None:
                prog.append(func)
        return sequentially(prog)(env)
    except:
        print "Error !"
        return None

if __name__ == "__main__":
    from sys import argv, stdin

    inFile = stdin
    if len(argv) > 1:
        inFile = open(argv[1])
    retval = logo_eval(inFile.read())
    print " =>", retval

