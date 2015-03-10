from logo import Primitive, Evaluator, Env, UnterminatedExpression, ProgramError, ParseError
from sys import argv, stdin
from zumoturtle import forward, backward, turnLeft, turnRight, setSpeed
import traceback
import math

def repl_init_readline(interpreter):
    def get_completion(text, state):
        match = filter(lambda x: x.startswith(text), interpreter.env.keys())
        try:
            return match[state]
        except IndexError as err:
            return None

    try:
        import readline
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode emacs')
        readline.set_completer(get_completion)
    except Exception as err:
        print "Error with readline lib (no advanced edition features)" + str(err)


def repl(interpreter, user_input=raw_input):
    repl_init_readline(interpreter)

    text, prompt = "", " > "
    while True:
        try:
            text += user_input(prompt)
            retval = interpreter.eval(text)
            text, prompt = "", "> "
            print " =>", retval
        except UnterminatedExpression:
            text += "\n"
            prompt = " ... "
        except ParseError as err:
            print "\033[31;1m[ERROR]\033[0m Syntax error in code"
            print "%s: %s" % (err.__class__.__name__, err)
            text, prompt = "", "> "
        except ProgramError as err:
            print "\033[31;1m[ERROR]\033[0m Error while running program"
            print "%s: %s" % (err.__class__.__name__, err)
            text, prompt = "", "> "
        except KeyboardInterrupt:
            print
            text, prompt = "", "> "
            continue
        except EOFError:
            print
            break

def main():
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
    else:
        repl(Evaluator(env=Env(**primitives_fr)))

if __name__ == "__main__":
    main()