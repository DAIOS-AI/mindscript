import sys
import ms
import readline
import argparse
from ms.ast import IncompleteExpression, Return, Exit
import ms.backend
import traceback

GREEN = "\033[32m"
BLUE = "\033[94m"
RED = "\x1B[31m"
RESET = "\033[0m"
WELCOME = """
MindScript Version 0.1 ({backend})
(C) 2024 DAIOS Technologies Limited
Use Control-D to exit.
"""

backends = [
    "llamacpp",
    "gpt35turbo",
    "gpt4turbo"
]

def execute_file(filename: str, backend: ms.backend.Backend):
    ip = ms.interpreter(backend=backend)
    code = ""

    try:
        with open(sys.argv[1], "r") as fh:
            code = fh.read()
        ip.eval(code)
    except Exception as e:
        print(e)
    
    exit(0)


def repl(backend: ms.backend.Backend):
    print(WELCOME)

    ip = ms.interpreter(interactive=True, backend=backend)

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
        except (Return, Exit):
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
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', type=str, help='an optional filename to process', default=None)
    parser.add_argument('--backend', help=f"choose backend from {backends}")
    args = parser.parse_args()

    if args.backend is not None and args.backend not in backends:
        print(f"Unknown backend: {args.backend}")
        exit(2)
    
    if args.backend is None or args.backend == "llamacpp":
        args.backend = "llamacpp"
        backend = ms.backend.LlamaCPP()
    elif args.backend == "gpt35turbo":
        backend = ms.backend.GPT3Turbo()
    elif args.backend == "gpt4turbo":
        backend = ms.backend.GPT4Turbo()
    else:
        backend = ms.backend.LlamaCPP()
    WELCOME = WELCOME.format(backend=args.backend)

    # Check if filename is provided as command-line argument
    if args.filename:
        execute_file(args.filename, backend)
    else:
        repl(backend)
