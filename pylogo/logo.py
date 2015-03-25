"""
A minimalist LOGO interpreter written in Python by iTitou.

Example LOGO program

    pour carre :taille
        repete 4 [ av :taille dr 90 ]
    fin

    repete 10 [carre 10 dr 36]
"""

import math
import re

# http://slps.github.io/zoo/logo/sdf.html

class ParseError(Exception):
    pass

class UnterminatedExpression(ParseError):
    pass

class ProgramError(Exception):
    pass

class UnknowIdentifier(ProgramError):
    pass

class TrollException(ProgramError):
    pass


class Env(object):
    """An environment object, referencing its outer environment"""

    def __init__(self, parent=None, *callables, **content):
        self.parent = parent
        self.content = {k: v for k, v in content.iteritems()}
        for func in callables:
            self.content[func.name] = func

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

    def keys(self):
        res = set(self.content.keys())
        if self.parent:
            res = res | self.parent.keys()
        return res

    @classmethod
    def lookup(klass, name):
        """Return a lambda(env) -> env[name]"""
        return lambda env: env[name]

class Callable(object):
    def __init__(self, name):
        self.name = name

class Procedure(Callable):
    """A user defined procedure, with named arguments"""

    def __init__(self, arg_names, body, name=''):
        super(Procedure, self).__init__(name)
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

    def __init__(self, func, arity=1, name=''):
        super(Primitive, self).__init__(name)
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
        n = times(env)
        for i in range(n):
            func(env)
        return n
    return f

def conditional(condition, consequence, alternate):
    def f(env):
        if condition(env):
            return consequence(env)
        else:
            return alternate(env)
    return f

def logo_while(condition, body):
    def f(env):
        while condition(env):
            body(env)
    return f

class Evaluator(object):
    Keywords_fr = {
        "LOOP": "repete", 
        "DEF_PROC": "pour",
        "END_PROC": "fin",
        "IF": "si", 
        "ELSE": "sinon",
        "MAKE_VAR": "donne",
        "WHILE": "tantque"
    }

    Builtin_operators = {
        "+": Primitive(lambda a,b: a+b, 2, '+'),
        "-": Primitive(lambda a,b: a-b, 2, '-'),
        "*": Primitive(lambda a,b: a*b, 2, '*'),
        "/": Primitive(lambda a,b: a/b, 2, '/'),
        "<": Primitive(lambda a,b: a<b, 2, '<'),
        "<=": Primitive(lambda a,b: a<=b, 2, '<='),
        "=": Primitive(lambda a,b: a==b, 2, '='),
        ">=": Primitive(lambda a,b: a>=b, 2, '>='),
        ">": Primitive(lambda a,b: a>b, 2, '>'),
    }

    Builtin_primitives = {
        "sin": Primitive(math.sin, 1, "sin"),
        "cos": Primitive(math.cos, 1, "cos"),
        "tan": Primitive(math.tan, 1, "tan"),
    }

    Builtin = {}
    Builtin.update(Builtin_operators)
    Builtin.update(Builtin_primitives)

    def __init__(self, env=None, keywords=Keywords_fr):
        self.env = Env(parent=env, **self.Builtin)
        self.keywords = keywords

    def analyze_number(self, numbrepr, tokens, i):
        res = None
        try:
            res = const(int(numbrepr))
        except ValueError:
            res = const(float(numbrepr))
        return res, i

    def analyze_list(self, tokens, i):
        expr = []
        try:
            while tokens[i] != "]":
                e, i = self.analyze(tokens, i)
                expr.append(e)
        except IndexError:
            raise UnterminatedExpression("Unterminated list")
        
        return logo_list(expr), i+1

    def analyze_procedure(self, tokens, i):
        try:
            name = tokens[i]
            i += 1
            args = []
            while tokens[i][0] == ':':
                args.append(tokens[i])
                i += 1

            # Create procedure in env for recursion...
            self.env[name] = Procedure(args, const(None), name)

            funcs = []
            while tokens[i] != self.keywords["END_PROC"]:
                f, i = self.analyze(tokens, i)
                funcs.append(f)
            body = sequentially(filter(lambda x: x is not None, funcs))
            
            # Then bind its actual body
            self.env[name].body = body
            return None, i+1
        except IndexError:
            raise UnterminatedExpression("Unterminated procedure definition")

    def analyze_var(self, tokens, i):
        try:
            name = tokens[i]
        except IndexError:
            raise UnterminatedExpression("Missing variable name")

        try:
            value, i = self.analyze(tokens, i+1)
        except IndexError:
            raise UnterminatedExpression("Missing variable value")
        self.env[name] = value(self.env)
        return None, i

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
            msg = "Missing arguments in call to %s. Expected %d; got %d" % (
                procedure.name, procedure.arity, len(args))
            raise UnterminatedExpression(msg)
        return lambda env: procedure.call(env, map(lambda x: x(env), args)), i

    def analyze_repetition(self, tokens, i):
        try:
            times, i = self.analyze(tokens, i)
        except IndexError:
            raise UnterminatedExpression("Missing loop count")
        try:
            expr, i = self.analyze(tokens, i)
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

    def analyze_infix_operator(self, operand, tokens, i):
        op = tokens[i]
        proc = self.Builtin_operators[op]
        try:
            other, i = self.analyze(tokens, i+1)
        except IndexError:
            raise UnterminatedExpression("Missing operand for " + op)
        return lambda env: proc.call(env, (operand(env), other(env))), i

    def analyze_parenthesis(self, tokens, i):
        expr = None
        try:
            expr, i = self.analyze(tokens, i)
        except IndexError:
            raise UnterminatedExpression("Missing expression after '('")
        if i >= len(tokens) or tokens[i] != ')':
            raise UnterminatedExpression("Missing matching ')'")
        return expr, i+1

    def analyze_while(self, tokens, i):
        try:
            cond, i = self.analyze(tokens, i)
        except IndexError:
            raise UnterminatedExpression("Missing condition for while")
        try:
            body, i = self.analyze(tokens, i)
        except IndexError:
            raise UnterminatedExpression("Missing body for while")
        return logo_while(cond, body), i

    def analyze(self, tokens, i):
        """
        analyze(tokens, index) -> (lambda(env), next index)
        """
        res = None
        tok = tokens[i].lower()
        i += 1

        if tok[0].isdigit():
            res, i = self.analyze_number(tok, tokens, i)

        elif tok == '"':
            res, i = self.analyze_string(tokens, i)

        elif tok == '[':
            res, i = self.analyze_list(tokens, i)

        elif tok == '(':
            res, i = self.analyze_parenthesis(tokens, i)

        elif tok == self.keywords["IF"]:
            res, i = self.analyze_if(tokens, i)

        elif tok == self.keywords["LOOP"]:
            res, i = self.analyze_repetition(tokens, i)

        elif tok == self.keywords["DEF_PROC"]:
            res, i = self.analyze_procedure(tokens, i)

        elif tok == self.keywords["MAKE_VAR"]:
            res, i = self.analyze_var(tokens, i)

        elif tok == self.keywords["WHILE"]:
            res, i = self.analyze_while(tokens, i)

        elif tok in self.env and isinstance(self.env[tok], Callable):
            res, i = self.analyze_call(self.env[tok], tokens, i)
            
        else:
            res, i = Env.lookup(tok), i

        if i < len(tokens) and tokens[i] in self.Builtin_operators:
            res, i = self.analyze_infix_operator(res, tokens, i)

        return res, i

    def eval(self, text):
        text = re.sub(r';.*\n', ' ', text)
        tokens = re.sub(r'([<>]=?|=|"|\(|\)|\[|\]|\+|\-|\*|\/)', " \\1 ", text).split()
        i, prog = 0, []
        while i < len(tokens):
            func, i = self.analyze(tokens, i)
            if func is not None:
                prog.append(func)
        return sequentially(prog)(self.env)
