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

MindScript is dynamically typed: only the values have a type, not the variables.

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

### Control structures

There are only three control structures in MindScript:
- logical expressions
- if-then expressions
- for-loop expressions
- (there are no while loops)

**Logical expressions** are short-circuited: as soon as the truth value is
known, the remaining subexpressions are not evaluated. For instance:
```
(2/1 == 1) or (2/2 == 1) or (2/3 == 2)
```
will only evaluate up to `(2/2 == 1)`, omitting the evaluation of `(2/3 == 2)`.

**If-then** expressions have a simple `if ... then` block structure:
```
if n == 1 then
    print("The value is 1.")
elif n == 2 then
    print("The value is 2.")
else
    print("The value is unknown.")
end
```

**For-loops** come in three forms: iteration over the elements of an array,
over the key-value pairs of an object, and over the non-null outputs of
an *iterator* (see below).
```
for let v in [1, 2, 3] do
    print(v)
end

for [let key, let value] in {"x": 1, "y": 2, "z": 3}
    print("(key, value) = " + str(key, value))
end

for let v in iter do
    print(v)
end
```

An iterator is a "function" of type `Null -> Any` that generates a sequence
of values. These are typically implemented using closures. The for loop will
repeatedly call an iterator `iter` as `iter()` until it returns a `null` value.

The entire for-loop evaluates to the last evaluated expression, i.e. as if
the executions of its body had been concatenated.







