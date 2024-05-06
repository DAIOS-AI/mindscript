import re
import sys
import ms
import readline
from ms.ast import IncompleteExpression, Return
import traceback

GREEN = "\033[32m"
BLUE = "\033[94m"
RED = "\x1B[31m"
RESET = "\033[0m"
WELCOME = """
MindScript Version 0.1
(C) 2024 DAIOS Technologies Limited
Use Control-D to exit.
"""


def execute_file(filename: str):
    ip = ms.interpreter()
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
    ip = ms.interpreter(interactive=True)

    prompt = "> "
    lines = ""
    while True:
        try:
            line = input(prompt)
            lines += "\n" + line
            res = ip.eval(lines)
            if res is None:
                continue
            repr = ip.printer.print(res)
            if res.annotation is not None:
                print(f"{GREEN}{res.annotation}")
            print(f"{BLUE}{repr}{RESET}")
            prompt = "> "
            lines = ""
        except IncompleteExpression:
            prompt = "| "
        except Return:
            print("\nExiting...")
            exit(0)
        except EOFError:
            print()
            exit(0)
        except KeyboardInterrupt:
            print("<Cancel input>")
            prompt = "> "
            lines = ""
        except Exception as e:
            print(f"{RED}{traceback.format_exc()}{RESET}")
            prompt = "> "
            lines = ""


if __name__ == "__main__":
    # Check if filename is provided as command-line argument
    if len(sys.argv) == 2:
        execute_file(sys.argv[1])
    else:
        repl()
