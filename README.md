<img src="media/mindscript-logo.svg" width="500px">

# MindScript

An experimental programming language combining formal and informal computation.

&copy; 2024 DAIOS Technologies Limited

![preview](media/screenshot.png)

## Table of Contents
<ul>
<li><a href="#description">Description</a></li>
<li><a href="#installataion">Installation</a></li>
<li><a href="#basics">Basics</a></li>
<li><a href="#operators">Operators</a></li>
<li><a href="#functions">Functions</a></li>
<li><a href="#control-structures">Control structures</a></li>
<li><a href="#destructuring">Destructuring</a></li>
<li><a href="#types">Types</a></li>
<li><a href="#formal-types">Formal types</a></li>
<li><a href="#informal-types">Informal types</a></li>
<li><a href="#oracles">Oracles</a></li>
<li><a href="#standard-library">Standard Library</li>
</ul>

## Description

MindScript is a programming language that gives both formal and 
informal computation first-class status, seamlessly integrating 
them. This approach allows developers to tailor the precision level 
of their coding based on the clarity about the solution.

MindScript lets programmers code directly when the method for 
accomplishing a task is clear. Conversely, when they know what 
they want but not how to achieve it, developers can simply 
describe their intent. For example, initially, one might outline the 
steps of a program, allowing MindScript simulate a preliminary, 
though possibly imperfect, implementation. As solutions become clearer,
this can later be refined with precise code. Additionally, 
for certain functions, such as analyzing the sentiment of a sentence, 
there might not exist a concrete implementation at all. 
The syntax is designed to make such specifications straightforward, 
providing simple yet powerful tools to express such concepts.

A distinctive feature of MindScript is its dual support for both 
formal and informal types. While formal types set hard constraints 
that can be algorithmically verified, informal types offer flexible 
inductive constraints, similar to how our observations guide our own thought 
processes.

In practice, formal computation within MindScript is realized through 
a Turing-complete language (&lambda;), ensuring rigorous programmability. 
Meanwhile, informal computations are handled by an oracle, realized through 
a language model (&Psi;) which interprets and processes less structured inputs. 
This dual approach allows MindScript to blend precision and flexibility.

**Features:**

- Implements an [oracle machine](https://en.wikipedia.org/wiki/Oracle_machine).
- Minimal C-like/JavaScript/Lua syntax on top of JSON data types.
- Everything is an expression.
- The formal type system is:
   - dynamic (runtime-checked),
   - structural (based on the properties, not on names or object hierarchies),
   - and strong (type rules are strictly enforced).
- Code comments are informal type annotations.
- (Current version) interpreter implemented in Python.


**Applications:**

- Processing of unstructured information
- Language model agents
- Semantic web
- and much more.

**Requirements:**

- Tested with Python 3.9
- [llama.cpp](https://github.com/ggerganov/llama.cpp/) to run the system locally, **or** an OpenAI API key to use a remote LLM.

**Disclaimer:**

This is a strictly experimental programming language. The Python implementation has likely bugs
and is does not aim to be efficient, only to demonstrate the concept. But if there's enough 
interest, I will write a runtime in C.

## Installation

MindScript requires access to an LLM, which is either local or remote.

### Running localy with llama.cpp:

Follow the instructions to install [llama.cpp](https://github.com/ggerganov/llama.cpp/)
and download your favorite model weights. For instance:

```
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
mkdir models
wget https://huggingface.co/QuantFactory/Meta-Llama-3-8B-GGUF/resolve/main/Meta-Llama-3-8B.Q8_0.gguf models/Meta-Llama-3-8B.Q8_0.gguf
```

Run the llama.cpp server. For instance: 
```
./server -m models/Meta-Llama-3-8B.Q8_0.gguf
```

Mindscript expects the llama.cpp server to run at `http://localhost:8080/completion`.

### Running remote with an OpenAI model:

Set the OpenAI API key as an environment variable:
```
export OPENAI_API_KEY=[YOUR API KEY]
```

## Installing and running MindScript

Install MindScript into a directory of your choice by cloning the Git repo:
```
git clone https://github.com/DAIOS-AI/mindscript/
cd mindscript
```

To run the REPL with e.g. GPT 3.5 turbo, enter
```
python mindscript.py --backend gpt35turbo
```

To run a program `myprogram.ms` with e.g. Llama.cpp, enter
```
python mindscript.py myprogram.ms --backend llamacpp
```

If you need help, enter
```
python mindscript.py -h
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

Variables are lexically scoped. The following code
```
let a = "outer a"
let b = "outer b"

do
    let a = "inner a"
    print(a)
    print(b)
end

print(a)
print(b)
```
outputs
```
inner a
outer b
outer a
outer b
```
as the declaration of the variable `a` inside the block
shadows the outer variable named `a`.


### Operators

Most of the usual operators are available and they have the expected precedence rules:

```
= + - * / % == != < <= > >= not and or
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
    if n==0 do
        1
    else
        n * factorial(n - 1)
    end
end
```

Note that:
- The arguments and the output can have a type annotation. Omitted types are assumed
  to be equal to `Any`, which is the universal type.
- If no argument is provided in the function declaration, the `null` argument
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
- conditional expressions
- for-loop expressions
- (there are no while loops)

**Logical expressions** are short-circuited: as soon as the truth value is
known, the remaining subexpressions are not evaluated. For instance:
```
(2/1 == 1) or (2/2 == 1) or (2/3 == 2)
```
will only evaluate up to `(2/2 == 1)`, omitting the evaluation of `(2/3 == 2)`.

**Conditional** expressions have a simple `if ... do ... else ... end` block structure with the
familiar semantics:
```
if n == 1 do
    print("The value is 1.")
elif n == 2 do
    print("The value is 2.")
else
    print("The value is unknown.")
end
```
These evaluate to the condition which is fulfilled, or to `null` otherwise.

**For-loops** iterate over the outputs of an *iterator* (see below). 
The entire for-loop evaluates to the last evaluated
expression, i.e. as if the executions of its body were concatenated.

```
for v in iterator do
    print(v)
end
```

An iterator is a "function" of type `Null -> Any` that generates a sequence
of values. These are typically implemented using closures. The for loop will
repeatedly call `iterator()` until it returns a `null` value.

Iterators can be custom, or created from arrays and dictionaries using the
`iter(value: Any) -> Null -> Any` built-in function.

In addition, the flow of execution can be modified through
- `continue( expr )`, which evaluates to `expr` and initiates the next iteration,
- `break( expr )`, which evaluates to `expr` and exits the entire for-loop.

### Destructuring

Destructuring assignment is a syntax that permits unpacking the members of
an array or the properties of an object into distinct values.

```
[let x, let y] = [2, -3, 1]
```
After this assignment, `x == 2` and `y == -3`. The third element `1` gets ignored.

```
{name: let n, email: let e} = {id: 1234, email: "albert@einstein.org", name: "Albert"}
```
After this assignment, `n == "Albert"` and `e == "albert@einstein.org"`. The
property `id` gets ignored.

These can be arbitrarily nested.

## Types

### Formal types

The primitive built-in data types are:
- `Null`: the `null` value;
- `Bool`: booleans, either `true` or `false`;
- `Int`: integers like `42` and `101`;
- `Num`: floating-point numbers like `3.1459`;
- `Str`: strings, enclosed in double- or single quotes as in `"hello, world!"` or `'hello, world!'`;
- `Type`: the type of a type.

In addition, there are container types:
- Arrays, as in `[1, 2, 3]` of type `[Int]`;
- Objects (or dictionaries), as in `{name: "Albert Einstein", age: 76}` of type `{name: Str, age: Int}`;
- Function objects, e.g. `cos(x: Num) -> Num` of type `Num -> Num`;
- `Any`: an arbitrary type.

There are also enums, which are created by specifying the type and an exhaustive list of permitted values:
```
let TwoOutOfThree = type Enum([Int], [[1, 2], [1, 3], [2, 3]]) 
```

The `typeOf` function returns the type of a given expression:

```
> typeOf({name: "Albert Einstein", age: 76})

{ name: Str, age: Int }

> typeOf(print)

Any -> Any

> typeOf(typeOf)

Any -> Type
```

### Custom formal types

New types are built using the `type` keyword followed by a *type expression*:
```
let Person = type {
    name!: Str,
    email!: Str?,
    age: Int,
    hobbies: [Str]
}
```
These types are aliases of the underlying structure, hence two types with different
names are equal if their structures match. 

Once created, they can be used as a normal MindScript values of type `Type`:
```
> typeOf(Person)
Type

> isSubtype({name: "Albert", email: null}, Person)
true
```

Notes:
- Primitive type atoms: The primitive types are `Bool`, `Int`, `Num`, and `String`.
- The container types are built using delimiters `[...]` (arrays) or `{...}` (objects) 
  and then further specifying the types of their members. 
- Similarly, function types are indicated by an arrow `->` as in `(Int -> Str) -> Str`.
  To indicate an arbiraty functional structure, use `Any -> Any`.
- You can omit the quotes/double-quotes of keys if they follow the naming convention
  of variable names.
- Mandatory object properties are indicated using `!`. Hence, `name!: Str` is a required
  property, whereas `name: Str` isn't and can be omitted.
- Nullable elements are indicated using `?`. Thus, `Str?` is
  either equal to a string or `null`, whereas `Str` can only be a valid string.

## Informal types

A value can be annotated with an explanatory comment, which becomes its informal
type. Informal types do not have well-defined semantics, but they influence their
evaluation by an oracle (see the section on oracles). Comments are created by
the annotation operator `#` which attaches a string to the value of the following
expression: 

```
# The speed of light in meters per second.
let c = 299792458
```

Since the annotation gets attached to the value of the following expression, the next
code will produce a function of informal type "Computes the sum of two integers."
```
# Computes the sum of two integers.
let sum = fun(n: Int, m: Int) -> Int do
    n + m
end
```

Likewise, this allows annotating type expressions:
```
let Person = {
    # The name of the person.
    name!: Str,
    
    # The age of the person.
    age: Int
}
```

## Oracles

Like functions, oracles produce outputs from inputs, but they do so using induction.
Oracles are defined using the `oracle` keyword. For instance:

```
# Write the name of an important researcher in the given field.
let researcher = oracle(field: Str) -> {name: Str}
```
That's it!
This creates an anonymous oracle with formal type `Str -> {name: Str}` and informal
type "Write the name of an important researcher in the given field." guiding the
generation of the output (i.e. informal types get added to the LLM prompt).

We can then use the oracle as if it were a function:
```
> researcher("physics")

{"name" : "Albert Einstein"}

> researcher("biology")

{"name": "Charles Darwin"}
```
where the inputs and outputs should conform to the given formal type.

### Examples

To help with the induction process one can also build the oracle
with examples. These are given using the `from` keyword plus an
array containing the examples.

```
let examples = [[0, "zero"], [1, "one"], [2, "two"], [3, "three"], [4, "four"], [5, "five"]]
let number2lang = oracle(number: Int) -> Str from examples
```
This time we did not provide a description of the task.

Then we can induce the output for a new input.
```
> number2lang(42)

"forty-two"

> number2lang(1024)

"one thousand twenty-four"
```
Obviously, since oracles perform inductive inference, they are not guaranteed 
to produce the correct output as in the previous case.

Each example must have the format `[arg_1, arg_2, ..., arg_n, output]`. For instance,
`[3, 2, "five"]` is a valid example for a function of type `Int -> Int -> Str`.

## Standard Library

MindScript fires up with a set of pre-loaded functions. 

To obtain an object that shows all the variables defined, use `getEnv`:
```
> getEnv()

{
    "dirFun": obj:{} -> [Str],
    "mute": _:Any -> Null,
    "dir": obj:{} -> [Str],
    "netImport": url:Str -> {},
    "www": url:Str -> Str?,
    "natural0": _:Null -> (Null -> Int?),
    "natural": _:Null -> (Null -> Int?),
    "range": start:Int -> stop:Int? -> (Null -> Int?),
    "reduce": f:(Any -> Any -> Any) -> iterator:(Null -> Any) -> Any,
    "filter": cond:(Any -> Bool) -> iterator:(Null -> Any) -> (Null -> Any),
    "map": f:(Any -> Any) -> iterator:(Null -> Any) -> (Null -> Any),
    "http": params:HTTPParams? -> method:Str? -> url:Str -> {},
    ...
```

You can import modules using `import` (local filesystem) or `netImport` (remote modules).
For instance, try importing the language module provided with the standard library.
```
> let lang = import("ms/lib/lang.ms")

{
    "write": instruction:Str -> {result: Str}?,
    "similarity": text1:Str -> text2:Str -> Similarity?,
    "similarityExamples": [
    ...
```

The functions become available through the object `lang`. First we list its properties:
```
> dir(lang)

[
    "write",
    "similarity",
    "similarityExamples",
    "Similarity",
    "keywordsExamples",
    "keywords",
    "coref",
    ...
```

Now let's try keyword extractor:
```
> lang.keywords("JavaScript is a high-level, often just-in-time compiled language that conforms
  to the ECMAScript standard.")

{
    "keywords": [
        "JavaScript",
        "high-level",
        "just-in-time compiled",
        "language",
        "ECMAScript standard"
    ]
}

```

To explore the standard library, just type the name of an object - the informal type annotation will
provide information about what it does.
```
> unshift

Pops the first value from the array.
array:[Any] -> Any

> http

Makes an HTTP request.
params:HTTPParams? -> method:Str? -> url:Str -> {}

> HTTPParams
type {
    mode: Str?,
    cache: Str?,
    credentials: Str?,
    headers: {

    }?,
    redirect: Str?,
    referrerPolicy: Str?,
    body: {

    }
}
```

## Explore

Explore the code of the library:
- [std.ms](https://github.com/DAIOS-AI/mindscript/blob/main/ms/lib/std.ms) the standard library,
  providing examples of function implementations.
- [lang.ms](https://github.com/DAIOS-AI/mindscript/blob/main/ms/lib/lang.ms) the language library,
  which contains many examples of oracles created with and without examples.






