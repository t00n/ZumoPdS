from logo import Primitive, Evaluator, Env, UnterminatedExpression, ProgramError, ParseError, TrollException, UnknowIdentifier
from sys import argv, stdin
from zumoturtle import forward, backward, turnLeft, turnRight, getGroundSensor, playMusic, getGroundSensorSum, groundPurple, groundBlack, groundPurpleRight, groundPurpleLeft, groundPurpleCenter, groundBlackRight, groundBlackLeft, groundBlackCenter, BLACK_THRES
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

    first_prompt = " \001\033[1m\002(\001\033[31m\002l\001\033[32m\002o\001\033[33m\002g\001\033[34m\002o\001\033[0;1\002m)\001\033[0m \002> "
    cont_prompt  = "    ... > "
    text, prompt = "", first_prompt
    while True:
        try:
            text += user_input(prompt)
            retval = interpreter.eval(text)
            text, prompt = "", first_prompt
            if retval is not None:
                print " =>", retval
        except UnterminatedExpression:
            text += "\n"
            prompt = cont_prompt
        except UnknowIdentifier as err:
            print "\033[31;1mJe ne sais pas ce qu'est \033[33m%s\033[0m" % (err)
            text, prompt = "", first_prompt
            playMusic()
        except UnknowIdentifier as err:
            print "\033[31;1mJe ne sais pas ce qu'est \033[33m%s\033[0m" % (err)
            text, prompt = "", first_prompt
            playMusic()
        except TrollException as err:
            print "\033[1;33m", str(err), "\033[31mc'est beaucoup trop grand Oo\033[0m"
            text, prompt = "", first_prompt
        except KeyboardInterrupt:
            print
            text, prompt = "", first_prompt
            continue
        except EOFError:
            print
            break
        except Exception as err:
            if "invalid literal" in str(err):
                litteral = str(err).split(':')[-1].strip()
                print "\033[31;1mJe ne comprends pas le nombre \033[33m%s\033[0m" % (litteral)
                playMusic()
            else:
                print "\033[31;1m[ERROR]\033[0m", "%s: %s" % (err.__class__.__name__, err)
            text, prompt = "", first_prompt

def main():

    def wrap_print(text):
        print text

    def preventTroll(func):
        """Not funny to have high forward values"""
        def f(*args):
            for arg in args:
                if arg > 1000:
                    raise TrollException(arg)
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
        P(groundPurpleRight, 0, "mauvedroite"), P(groundBlackRight, 0, "noirdroite"),
        P(groundPurpleLeft, 0, "mauvegauche"), P(groundBlackLeft, 0, "noirgauche"),
        P(groundPurpleCenter, 0, "mauvecentre"), P(groundBlackCenter, 0, "noircentre"),
        P(getGroundSensor, 1, "sol"), P(getGroundSensorSum, 0, "lesol"),
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