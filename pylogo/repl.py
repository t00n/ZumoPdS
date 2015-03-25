from logo import Primitive, Evaluator, Env, UnterminatedExpression, ProgramError, ParseError, TrollException
from sys import argv, stdin
from zumoturtle import forward, backward, turnLeft, turnRight, getGroundSensor, playMusic
import traceback
import math
import os

Autocomplete = []

def repl_init_readline(interpreter):
    def get_completion(text, state):
        global Autocomplete
        if state == 0:
            Autocomplete = filter(lambda x: x.startswith(text), interpreter.env.keys())
        return Autocomplete[state]
        try:
            return match[state]
        except IndexError as err:
            return None

    try:
        import readline
        import atexit

        histfile = os.path.join(os.path.expanduser("~"), ".logo_repl")
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        atexit.register(readline.write_history_file, histfile)

        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode emacs')
        readline.set_completer(get_completion)
    except Exception as err:
        print "\033[1;33m[WARNING]\033[0m Cannot setup readline:", str(err)
        print "      ... No advanced command-line edition features"


def repl(interpreter, user_input=raw_input):
    repl_init_readline(interpreter)

    first_prompt = " \033[1m(\033[31ml\033[32mo\033[33mg\033[34mo\033[0;1m)\033[0m > "
    cont_prompt  = "    ... > "
    text, prompt = "", first_prompt
    while True:
        try:
            text += user_input(prompt)
            retval = interpreter.eval(text)
            text, prompt = "", first_prompt
            print " =>", retval
        except UnterminatedExpression:
            text += "\n"
            prompt = cont_prompt
        except ParseError as err:
            print "\033[31;1m[ERROR]\033[0m Syntax error in code"
            print "%s: %s" % (err.__class__.__name__, err)
            text, prompt = "", first_prompt
            playMusic()
        except ProgramError as err:
            print "\033[31;1m[ERROR]\033[0m Error while running program"
            print "%s: %s" % (err.__class__.__name__, err)
            text, prompt = "", first_prompt
            playMusic()
        except KeyboardInterrupt:
            print
            text, prompt = "", first_prompt
            continue
        except EOFError:
            print
            break
        except Exception as err:
            print "\033[31;1m[ERROR]\033[0m", "%s: %s" % (err.__class__.__name__, err)
            text, prompt = "", first_prompt

def main():
    BLACK_THRES = 1024

    def wrap_print(text):
        print text

    def groundSum():
        return sum(getGroundSensor(i) for i in range(6))

    def groundPurple():
        return groundSum() < BLACK_THRES

    def groundBlack():
        return groundSum() >= BLACK_THRES

    def preventTroll(func):
        """Not funny to have high forward values"""
        def f(*args):
            for arg in args:
                if arg > 1000:
                    raise TrollException("Number too high")
            return func(*args)
        return f

    P = Primitive
    T = preventTroll

    primitives_fr = (
        P(T(turnLeft), 1, "ga"),  P(T(turnLeft), 1, "gauche"),
        P(T(turnRight), 1, "dr"), P(T(turnRight), 1, "droite"),
        P(T(forward), 1, "av"),   P(T(forward), 1, "avance"),
        P(T(backward), 1, "re"),  P(T(backward), 1, "recule"),
        P(wrap_print, 1, "p"), P(wrap_print, 1, "print"),
        P(groundPurple, 0, "mauve"), P(groundBlack, 0, "noir"),
        P(getGroundSensor, 1, "sol"), P(groundSum, 0, "lesol"),
        P(math.sqrt, 1, "racine"), P(math.sqrt, 1, "rc"),
        P(exit, 0, "q"), P(exit, 0, "quit"),
    )

    if len(argv) > 1:
        for script in argv[1:]:
            try:
                retval = Evaluator(env=Env(None, *primitives_fr)).eval(open(script).read())
            except Exception as err:
                print "\033[1;31m[ERROR]\033[0m in execution of", script, ":", str(err)
                traceback.print_exc()
    else:
        repl(Evaluator(env=Env(None, *primitives_fr)))

if __name__ == "__main__":
    main()