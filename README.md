# LIJP language & RPython-runtime for it

LIJP is a member of lisp programming languages
designed to be a backend for a statically typed, lazy,
pure functional programming language.

## Language description

Describing the abstract syntax for the language with Haskell:

    data Term = Var Natural
              | App Term Term
              | Abs Term
              | Let [Term] Term
              | Enum Natural Natural
              | Case Term [Term]

Syntax is simple enough:

 1. Variables are denoted with sequences of digits.
 2. Parentheses are used as grouping element.
 3. Sequences of terms are interpreted as application
 4. Lambda abstraction is denoted by lambda symbol(`λ`).
 5. Let expression is expressed with terms separated by colon(`:`),
    multiple binds happening in parallel are separated by comma(`,`).
 6. Data constructor is an index separated from arity with a slash(`/`).
    The index and arity are digit sequences.
 7. Case expression is a term followed by braces (`{}`),
    enclosing cases separated by semicolon (`;`)
 8. Hash (`#`) is used as a single-line comment.
 9. Whitespace is ignored unless it separates two terms.

_2020-09-30 update:_ `Let Term Term` changed to `Let [Term] Term`.
The parallel bind informs that the bound terms won't reference each other.

## Sample programs

### SKI -combinators

These combinators should be relatively familiar to everybody:
Here's the S -combinator.

    λλλ2 0 (1 0)

The K -combinator:

    λλ1

The I -combinator:

    λ0


### Fixed point combinator

    λ (λ1(0 0)) (λ1(0 0))

### Boolean arithmetic

      (λλ1{ 0; 1/0 })  # or
    , (λλ1{ 0/0; 0 })  # and
    , (λ0{ 1/0; 0/0 }) # not
    : 0 (0 (0 (0 (2 0/0 0/0)))) # not (not (not (not (or false false))))

## RPython runtime

The runtime implements some barebones functionality
for evaluating lijp programs.

 1. The `runtime/term.py` reads terms and implements the lijp syntax.
 2. The `runtime/evaluator.py` implements a lazy evaluator.

### How to build

 1. Ensure you have Python installed.
 2. Download the pypy runtime and extract it.
 3. Locate the rpython and run it on the `runtime/goal_standalone.py`.

Sequence of terminal commands that do the trick:

    wget https://downloads.python.org/pypy/pypy3.6-v7.3.2-src.tar.bz2
    tar -xf pypy3.6-v7.3.2-src.tar.bz2
    pypy3.6-v7.3.2-src/rpython/bin/rpython runtime/goal_standalone.py 

On successful compile you obtain the `lijp` -executable.
You can try out some of the samples by running it there:

    ./lijp samples/boolean-arithmetic.ij
    ./lijp samples/s-combinator.ij

It doesn't produce particularly interesting outputs.
It currently just prints "Returned a tag 0" or "Returned non-integer non-tag".

### Internal structure of the interpreter with some design objectives

Both the evaluator and term reader could be accessible from the runtime.

The `obj.RuntimeTypeError` is raised whenever there's any kind of an error.

There are primitives `obj.Integer` and `obj.Data`
to pass around primitive data types
plus some functions to typecheck the structures,
called `obj.to_integer` and `obj.to_data`.

It's expected that lists are built from constructors,
expecting tag 0 for the empty list, and tag 1 for the populated list.
The `obj.from_list`/`obj.to_list` convert


#### Starting process

The prelude is passed to the program as a script.
It's either coming through standard input,
or from a file given as the first argument.

There is no I/O driver in the runtime.
Program is just evaluated and it tries to read it as a value.

The startup process is implemented by the `runtime/goal_standalone.py`.

#### Evaluator

The interpreter is using the push/enter evaluation model.
Internally `object.enter(argument_list)` is expected to be used.
This procedure may return a primitive or then a `evaluator.PAP` -structure.
In case it does neither then it likely crashes or hangs up.

`evaluator.Prog(env, expr)` is an unevaluated expression object.

The `evaluator.PAP(obj, args)` is a partially applied function object,
this is produced whenever a function is entered with too few arguments.

The `evaluator.Thunk(obj)` implements lazy evaluation.
Upon evaluation the thunk rewrites itself into the computation result
procuded by the heap object it refers to.

The evaluator has several entry points,
though I prefer the `evaluator.activate(env, expr)` would be used.
This procedure produces a construct to evaluate an expression
and determines whether a thunk is needed in the expression.

The `evaluator.examine(expr)` determines whether to
build a thunk for the expression or not.

The `evaluator.evaluate(env, expr, args)` starts an on-demand
evauluation of an expression,
inside the given environment with the given arguments.

#### Loader

The loader is considerably uninteresting.
It is used by constructing a `term.Reader()` -state.
Then run `term.read_character(reader, char)`
through every character and finally call `term.read_done(reader)`
to terminate reading and obtain the read term as the result.
The state is discarded after use.

Reader procudes `term.ReadError(char)` upon a failure.

The term produced by the reader is a runtime-readable data structure
closely following the abstract syntax encoding of lijp.

## Motivation

Lijp is an exploration tool based on the observation
that some dynamically typed languages form a feasible runtime
for a statically typed pure functional programming language.

The focus of this project is the use of types as user interface elements
and treating of typechecking as something
that verifies that some plan is feasible to apply.

Large programs would become systems for running many small programs
written by the users of mentioned systems.
