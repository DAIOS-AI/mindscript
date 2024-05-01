![mindscript](media/mindscript.png)

# MindScript

An experimental programming language combining formal and informal computation.

(C) 2024 DAIOS Technologies Limited

## Description

MindScript is a programming language with both formal and informal
computation as first class citizens. Formal computation is implemented as
a Turing-complete programming language (&lambda;), while informal computation is 
obtained by consulting an oracle, implemented as a large language model (&Psi;).

Features:

- MindScript implements an [oracle machine](https://en.wikipedia.org/wiki/Oracle_machine).
- Minimal C-like/JavaScript syntax on top of JSON data types.
- Runtime type checking.
- Code comments are semantic type annotations.
- (Current version) implemented in Python.


Applications:

- Processing of unstructured information
- Language model agents
- Semantic web
- and much more.

Requirements:

- Tested with Python 3.9

## Quickstart

To run the REPL, enter
```
> python mindscript.py
```

To run a program `myprogram.ms`, enter
```
> python mindscript.py myprogram.ms
```

## Examples

```
# "Determine the distance of the planet from the sun in astronomical units."
let au = function(planet: Str) -> Num oracle

au("earth") 
au("mars")
```


