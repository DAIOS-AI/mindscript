![mindscript](media/mindscript.png)

# MindScript

An experimental programming language combining formal and informal computation.

(C) 2024 DAIOS Technologies Limited

![preview](media/screenshot.png)

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

## Basics

MindScript is dynamically typed --- only the values (but not the variables)
have a type. 

```
let greeting = "Hello, world!"

```

This defines a variable named `greeting` containing a value `Hello, world!` of type `Str`.

Everything is an expression. For instance, all of the following expressions evaluate
to `42`:

```
42
(40 + 2)
print(42)
let my_variable = 42
```

### Formal data types

The basic data types are:
- `Null`: the `null` value;
- `Bool`: booleans, either `true` or `false`;
- `Int`: integers like `42`;
- `Num`: floating-point numbers like `3.1459`;
- `Str`: strings, enclosed in double- or single quotes as in `"hello, world!"` or `'hello, world!'`;
- `Type`: the type of a type.

In addition, there are container types:
- `Array`: arrays, as in `[1, 2, 3]`;
- `Object`: objects or dictionaries, as in `{name: "Albert Einstein", age: 76}`;
- `Function`: function objects;
- `Any`: an arbitrary type.

The `typeof` function returns the type of a given expression:

```
> typeof({name: "Albert Einstein", age: 76})

{ name: Str, age: Int }

> typeof(print)

Any -> Any

> typeof(typeof)

Any -> Type
```

### Informal data types

A value can be annotated with an explanatory comment, which becomes its informal
type. Informal types do not have well-defined semantics, but they influence their
evaluation by the oracle (see the section on oracles). Comments are created by
the annotation operator `#` which attaches a string to the value of the following
expression: 

```
# "The speed of light in meters per second."
let c = 299792458
```


### Expressions

Most of the usual operators are available and they have the expected precedence rules:

```
+ - * / % == != < <= > >= not and or
```

Types aren't cast automatically, and applying an operator to values having incompatible
types will lead to runtime errors. 

### Functions

Functions are defined the `fun` keyword. This builds a lambda expression, hence the
functions are anonymous. Functions can have one of more arguments and they can be
typed. 

As an example, consider the factorial function:

```
let factorial = fun(n: Int) -> Int do
    if n==0 then 
        0
    else
        n * factorial(n - 1)
    end
end
```

Note that:
- The arguments and the output can have a type annotation. Omitted types are assumed
  to be equal to `Any`.
- If no argument is provided in the function declaration, the a `null` argument
  is added automatically.
- The body of the function is enclosed in a `do ... end` block containing
  expressions. The function returns the value of the last expression,
  unless an explicit `return([VALUE])` expression is provided.

Functions are curried. Thus, the function
```
let sum = fun(n: Int, m: Int) -> Int do
    return(n + m)
end
```

has type `Int -> Int -> Int`, that is, arguments are consumed one-by-one, 
producing intermediate functions as results, and the following works:
```
> sum(1, 3)
4

> let add_one = sum(1)
fun(m: Int) -> Int

> add_one(3)
4

> sum(1)(3)
4
```






