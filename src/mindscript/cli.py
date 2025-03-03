#!/usr/bin/env python

import readline # Necessary for a decent experience in the command line.
import io
import sys
import contextlib
import mindscript
import argparse
from mindscript.ast import IncompleteExpression, Return, Exit, SyntaxError, LexicalError
import mindscript.backend
import traceback


GREEN = "\033[32m"
BLUE = "\033[94m"
RED = "\x1B[31m"
RESET = "\033[0m"

WELCOME = """
MindScript Version {version} ({backend})
(C) 2024, 2025 DAIOS Technologies Limited
Use Control-D to exit.
"""

backends = [
    "llamacpp",
    "openai",
    "ollama"
]


def execute_file(filename: str, backend: mindscript.backend.Backend):
    ip = mindscript.interpreter(backend=backend)
    code = ""

    try:
        with open(filename, "r") as fh:
            code = fh.read()
        ip.eval(code, filename)
    except (Return, Exit):
        exit(0)
    except (SyntaxError, LexicalError, IncompleteExpression, EOFError):
        print("Reached end of file.")
        exit(1)
    except Exception as e:
        print(f"{RED}{traceback.format_exc()}{RESET}")

    exit(0)


def repl(backend: mindscript.backend.Backend, welcome):
    print(welcome)

    ip = mindscript.interpreter(interactive=True, backend=backend)

    prompt = "> "
    lines = ""
    stderr_buffer = io.StringIO()
    while True:
        try:
            line = input(prompt)
            lines += line + "\n"
            errmsg = ""
            with contextlib.redirect_stderr(stderr_buffer):
                res = ip.eval(lines, "<repl>")
                errmsg = stderr_buffer.getvalue()
            
            if errmsg != "":
                print(f"{RED}{errmsg}{RESET}", file=sys.stderr)
                stderr_buffer.truncate(0)
                stderr_buffer.seek(0)

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', type=str,
                        help='an optional filename to process', default=None)
    parser.add_argument('-b', metavar='BACKEND', help=f"chooses an LLM backend from {backends}")
    parser.add_argument('-u', metavar='URL', help=f"specifies the API's URL")
    parser.add_argument('-m', metavar='MODEL', help=f"specifies the name of the model to use")
    args = parser.parse_args()

    if args.b is not None and args.b not in backends:
        print(f"Unknown backend: {args.b}")
        exit(2)

    backend = None
    try:
        if args.b is None or args.b == "llamacpp":
            args.b = "llamacpp"
            backend = mindscript.backend.LlamaCPP(args.u)
        elif args.b == "openai":
            if args.m is None:
                print(f"The OpenAI backend requires a model name.")
                exit(2)
            backend = mindscript.backend.OpenAI(args.u, args.m)
        elif args.b == "ollama":
            if args.m is None:
                print(f"The Ollama backend requires a model name.")
                exit(2)
            backend = mindscript.backend.Ollama(args.u, args.m)
        else:
            backend = mindscript.backend.LlamaCPP()
    except Exception as e:
        print(e)
        exit(2)
    welcome = WELCOME.format(version=mindscript.__version__, backend=args.b)

    # Check if filename is provided as command-line argument
    if args.filename:
        execute_file(args.filename, backend)
    else:
        repl(backend, welcome)

