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

class ParseError(Exception):
    pass

class UnterminatedExpression(ParseError):
    pass

class ProgramError(Exception):
    pass

class UnknowIdentifier(ProgramError):
    pass


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
        raise UnknowIdentifier(key)

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

def const(value):
    """Return a lambda(env) returning a constant value"""
    return lambda env: value

def logo_list(expressions):
    return lambda env: map(lambda expr: expr(env), expressions)

def sequentially(functions):
    """
    Return a lambda(env) executing functions sequentially, 
    returning the last one retval
    """
    if len(functions) > 1:
        return lambda env: map(lambda f: f(env), functions).pop()
    elif len(functions) == 1:
        return functions[0]
    return const(None)

def repetition(times, func):
    """Return a lambda(env) executing a function multiple times"""
    def f(env):
        for i in range(times):
            func(env)
        return times
    return f

def conditional(condition, consequence, alternate):
    def f(env):
        if condition(env):
            return consequence(env)
        else:
            return alternate(env)
    return f

class Evaluator(object):
    Keywords_fr = {
        "LOOP": "repete", 
        "DEF_PROC": "pour",
        "END_PROC": "fin",
        "IF": "si", 
        "ELSE": "sinon",
    }

    Builtin_primitives = {
        "+": Primitive(lambda a,b: a+b, 2),
        "-": Primitive(lambda a,b: a-b, 2),
        "*": Primitive(lambda a,b: a*b, 2),
        "/": Primitive(lambda a,b: a/b, 2),
        "<": Primitive(lambda a,b: a<b, 2),
        "<=": Primitive(lambda a,b: a<=b, 2),
        "=": Primitive(lambda a,b: a==b, 2),
        ">=": Primitive(lambda a,b: a>=b, 2),
        ">": Primitive(lambda a,b: a>b, 2),
        "sin": Primitive(math.sin),
        "cos": Primitive(math.cos),
        "tan": Primitive(math.tan),
    }

    def __init__(self, env=None, keywords=Keywords_fr):
        self.env = Env(parent=env, **self.Builtin_primitives)
        self.keywords = keywords

    def analyze_list(self, tokens, i):
        expr = []
        try:
            while tokens[i] != "]":
                e, i = self.analyze(tokens, i)
                expr.append(e)
        except IndexError:
            raise UnterminatedExpression("Unterminated loop")
        
        return logo_list(expr), i+1

    def analyze_procedure(self, tokens, i):
        name = tokens[i]
        i += 1

        try:
            args = []
            while tokens[i][0] == ':':
                args.append(tokens[i])
                i += 1

            funcs = []
            while tokens[i] != self.keywords["END_PROC"]:
                f, i = self.analyze(tokens, i)
                funcs.append(f)
        except IndexError:
            raise UnterminatedExpression("Unterminated procedure definition")

        body = sequentially(filter(lambda x: x is not None, funcs))
        self.env[name] = Procedure(args, body)
        return None, i+1

    def analyze_string(self, tokens, i):
        words = []
        try:
            while tokens[i] != '"':
                words.append(tokens[i])
                i += 1
        except IndexError:
            raise UnterminatedExpression("Unterminated String")
        return const(" ".join(words)), i+1

    def analyze_call(self, procedure, tokens, i):
        args = []
        try:
            for argno in range(procedure.arity):
                arg, i = self.analyze(tokens, i)
                args.append(arg)
        except IndexError:
            raise UnterminatedExpression("Missing arguments in call")
        return lambda env: procedure.call(env, map(lambda x: x(env), args)), i

    def analyze_loop(self, tokens, i):
        try:
            times = int(tokens[i])
        except IndexError:
            raise UnterminatedExpression("Missing loop count")
        try:
            expr, i = self.analyze(tokens, i+1)
        except IndexError:
            raise UnterminatedExpression("Missing loop body")
        return repetition(times, expr), i

    def analyze_if(self, tokens, i):
        cond, i = self.analyze(tokens, i)
        cons, i = self.analyze(tokens, i)
        alt = const(None)
        if i < len(tokens) and tokens[i] == self.keywords["ELSE"]:
            alt, i = self.analyze(tokens, i+1)
        return conditional(cond, cons, alt), i

    def analyze(self, tokens, i):
        """
        analyze(tokens, index) -> (lambda(env), next index)
        """
        res = None
        tok = tokens[i].lower()
        i += 1

        if tok.isdigit():
            return const(int(tok)), i

        elif tok == '"':
            return self.analyze_string(tokens, i)

        elif tok == '[':
            return self.analyze_list(tokens, i)

        elif tok == self.keywords["IF"]:
            return self.analyze_if(tokens, i)

        elif tok == self.keywords["LOOP"]:
            return self.analyze_loop(tokens, i)

        elif tok == self.keywords["DEF_PROC"]:
            return self.analyze_procedure(tokens, i)

        elif tok in self.env and isinstance(self.env[tok], Callable):
            return self.analyze_call(self.env[tok], tokens, i)
            
        else:
            return Env.lookup(tok), i

    def eval(self, text):
        lines = filter(lambda line: not line.strip().startswith(';'), text.split('\n'))
        tokens = ' '.join(lines).replace('[', ' [ ').replace(']', ' ] ').replace('"', ' " ').split()
        i, prog = 0, []
        while i < len(tokens):
            func, i = self.analyze(tokens, i)
            if func is not None:
                prog.append(func)
        return sequentially(prog)(self.env)

    def repl(self, user_input=raw_input):
        text, prompt = "", " > "
        while True:
            try:
                text += user_input(prompt)
                retval = self.eval(text)
                text, prompt = "", "> "
                print " => ", retval
            except UnterminatedExpression:
                text += "\n"
                prompt = " ... "
            except ParseError as err:
                print "\033[31;1m[ERROR]\033[0m Syntax error in code"
                print "%s: %s" % (err.__class__.__name__, err)
            except ProgramError as err:
                print "\033[31;1m[ERROR]\033[0m Error in running program"
                print "%s: %s" % (err.__class__.__name__, err)
            except KeyboardInterrupt:
                print
                continue
            except EOFError:
                print
                break

if __name__ == "__main__":
    from sys import argv, stdin
    from zumoturtle import forward, backward, turnLeft, turnRight, setSpeed
    import traceback

    def wrap_print(text): 
        print text

    P = Primitive
    primitives_fr = {
        "ga": P(turnLeft),  "gauche": P(turnLeft),
        "dr": P(turnRight), "droite": P(turnRight),
        "av": P(forward),   "avance": P(forward),
        "re": P(backward),  "recule": P(backward),
        "vi": P(setSpeed),  "vitesse": P(setSpeed),
        "p": P(wrap_print), "print": P(wrap_print),
        "racine": P(math.sqrt), "rc": P(math.sqrt),
        "q": P(exit, 0),
    }

    if len(argv) > 1:
        for script in argv[1:]:
            retval = Evaluator(env=Env(**primitives_fr)).eval(open(script).read())
            print " =>", retval
    else:
        Evaluator(env=Env(**primitives_fr)).repl()

