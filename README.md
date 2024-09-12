## Introduction

This repository is a short summary of common typing problems and their solutions. Even though several `PEP` documents and `mypy` documentation provide a very good overview of the topic, the amount of production problems I encountered (which would not have happened with proper types) is disturbing.

I personally avoid using `from typing import Any, cast` and `# type: ignore[...]` as much as possible. If you work in a code base with little to no external libraries, then in **most** cases all typing problems are the outcome of bad code design.

## The benefits of statically typed code

Proper typing in python requires some experience, either in statically typed languages, or many different projects. Additionally in it's current state it can generate a lot of boilerplate code and slow down the development process (by keeping your code resistant to ugly hacks, but still). However every active `mypy` user will for sure agree, how much nicer the development is if the code base is properly typed. You no loger have to fear for every simple change, the compiler got your back.

### Dealing with args and kwargs with `Unpack`

When dealing with positional or keyword arguments of a single type, the solution is fairly simple:

```python
def test_function(*args: str, **kwargs: str) -> None:
    ...
```

This way we enforce, that all of the args and kwargs will be strings. But this does not even specify their amount... and what about the differing types?

```python
from typing_extensions import NotRequired, TypedDict, Unpack

class Kwargs(TypedDict):
    value_1: int
    value_2: str
    value_3: NotRequired[float]


def test_function(*args: Unpack[tuple[int, str]], **kwargs: Unpack[Kwargs]) -> None:
    ...
```

Using `Unpack` we can enforce the exact names and types of kwargs and the correct order and types of args.

### The lack of value and `Optional`

If you want to present the lack of a value, you can utilize an optional variable:

```python
from typing import Optional

def test_function(value: Optional[int]) -> int:
    return value if value is not None else 0
```

Not only will this inform users that a value might not exist, but also enforce them to perform a check when accessing it.

### What in case of no return... or `NoReturn`?

### Difference between `TypeAlias` and `NewType`

### Avoiding unnecessary imports with `TYPE_CHECKING`

### Type narrowing with `TypeGuard`

### Inheritance with `final` and `override`

### We have templates at home (with `Generic` and `TypeVar`)

### We have traits at home (with `Protocol`)

### Dealing with callables and callback protocols

### Dealing with decorators

```python
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

_P = ParamSpec("_P")
_R = TypeVar("_R")

def log_return_value(func: Callable[_P, _R]) -> Callable[_P, _R]:
    @wraps(func)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        result = func(*args, **kwargs)
        print("Result:", result)
        return result

    return inner
```

Accessing state with method decorators:

```python
from functools import wraps
from typing import Callable, Concatenate, ParamSpec, TypeVar

_P = ParamSpec("_P")
_R = TypeVar("_R")

class SomeClass:
    def do_something(self) -> None:
        ...

def call_do_something(meth: Callable[Concatenate[SomeClass, _P], _R]) -> Callable[Concatenate[SomeClass, _P], _R]:
    @wraps(meth)
    def inner(self: SomeClass, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        self.do_something()
        return meth(self, *args, **kwargs)

    return inner
```

### Signature `overload`
