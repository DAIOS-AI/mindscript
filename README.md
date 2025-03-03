
<img src="https://raw.githubusercontent.com/DAIOS-AI/mindscript/75e878fe319ada80fef43673b6b0fa73b334e18d/media/mindscript-logo-lambda-psi.svg" width="500px">

An experimental programming language combining formal and informal computation.

&copy; 2024, 2025 [Daios Technologies Limited](https://www.daios.ai)

![preview](https://mindscript.daios.ai/assets/mindscript-demo.png)


**Read the Docs:** [https://mindscript.daios.ai](https://mindscript.daios.ai) <br>
**Try in Browser:** [https://www.daios.ai/playground](https://www.daios.ai/playground) <br>
**Source code:** [https://github.com/DAIOS-AI/mindscript](https://github.com/DAIOS-AI/mindscript)

## Description

MindScript is a programming language that seamlessly integrates
both formal and informal computation.

MindScript lets programmers code directly when the method for 
accomplishing a task is clear. Conversely, when they know what 
they want but not how to achieve it, developers can simply 
describe their intent. Indeed, for certain functions, such as 
analyzing the sentiment of a sentence, there might not exist 
a concrete implementation at all. The syntax is designed to 
make such specifications straightforward.

A distinctive feature of MindScript is its dual support for both 
formal and informal types. The formal types are as in other programming
languages, which allow expressing hard constraints. The informal types
(unique to MindScript) on the other hand offer flexible
inductive constraints, similar to how our observations guide our own thought 
processes.

In practice, formal computation within MindScript is realized through 
a Turing-complete language (&lambda;), while informal computations are 
handled by an oracle, realized through a language model (&Psi;) which 
interprets and processes less structured inputs (hence &lambda;<sup>&Psi;</sup>). 


## Features

- Implements an [oracle machine](https://en.wikipedia.org/wiki/Oracle_machine).
- Minimal C-like/JavaScript/Lua syntax on top of JSON data types.
- Everything is an expression.
- The formal type system is:
    - dynamic (runtime-checked),
    - structural (based on the properties, not on names or object hierarchies),
    - and strong (type rules are strictly enforced).

- Code comments are informal type annotations.
- (Current version) interpreter implemented in Python.


## Applications

- Applications that use large language models
- Processing of unstructured information
- Language model agents
- Semantic web
- and much more.

## Requirements

- Python 3.9 or higher
- an LLM backend (see [installation](installation.md))



## Disclaimer

This is a strictly experimental programming language. The Python implementation does not
aim to be efficient and most likely contains bugs.

