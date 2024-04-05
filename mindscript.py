import re
import sys
import scripting
import readline
from scripting.ast import IncompleteExpression


BLUE = "\033[94m"
RESET = "\033[0m"
WELCOME = """
MindScript Version 0.1
(C) 2024 DAIOS Technologies Limited
Use Control-D to exit. Enter ';' to finish expression.
"""


def execute_file(filename: str):
    ip = scripting.interpreter()
    code = ""

    try:
        with open(sys.argv[1], "r") as fh:
            code = fh.read()
        ip.eval(code)
    except Exception as e:
        print(e)
    
    exit(0)


def repl():
    print(WELCOME)
    ip = scripting.interpreter(interactive=True)

    prompt = "> "
    lines = ""
    while True:
        try:
            line = input(prompt)
            lines += line + "\n"
            res = ip.eval(lines)
            repr = ip.printer.print(res)
            print(f"{BLUE}{repr}{RESET}")
            prompt = "> "
            lines = ""
        except IncompleteExpression:
            prompt = "| "
        except KeyboardInterrupt:
            print("\nExiting...")
            exit(0)
        except EOFError:
            print()
            exit(0)


if __name__ == "__main__":
    # Check if filename is provided as command-line argument
    if len(sys.argv) == 2:
        execute_file(sys.argv[1])
    else:
        repl()
