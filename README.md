![mindscript](media/mindscript.png)

# MindScript

An experimental programming language combining formal and informal computation.

(C) 2024 DAIOS Technologies Limited

## Description

MindScript is a programming language with both formal and informal
computation as first class citizens. Formal computation is implemented as
a Turing-complete programming language (&lambda;), while informal computation is 
obtained by consulting an oracle, implemented as a large language model (&Psi;).

**Features:**

- MindScript implements an [oracle machine](https://en.wikipedia.org/wiki/Oracle_machine).
- Minimal C-like/JavaScript syntax on top of JSON data types.
- Dynamically typed with runtime type checking.
- Code comments are semantic type annotations.
- (Current version) implemented in Python.


**Applications:**

- Processing of unstructured information
- Language model agents
- Semantic web
- and much more.

**Requirements:**

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

## Basics

MindScript is dynamically typed --- only the values (but not the variables)
have a type. 

```
let greeting = "Hello, world!"

```

This defines a variable named `greeting` containing a value `Hello, world!` of type `Str`.

Everything is an expression. For instance, all of the following expression evaluate
to `42`:

```
42
(40 + 2)
print(42)
let my_variable = 42
```

### Data types

The basic data types are:
- `Null`: the `null` value;
- `Bool`: booleans, either `true` or `false`;
- `Int`: integers like `42`;
- `Num`: floating-point numbers like `3.1459`;
- `Str`: strings, enclosed in double- or single quotes as in `"hello, world!"` or `'hello, world!'`;
- `Array`: arrays, as in `[1, 2, 3]`;
- `Object`: objects or dictionaries, as in `{name: "Albert Einstein", age: }`

```
```


