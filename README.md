## Introduction

This repository is a short summary of common typing problems and their solutions. Even though several `PEP` documents and `mypy` documentation provide a very good overview of the topic, the amount of production problems I encountered (which would not have happened with proper types) is disturbing.

I personally avoid using `from typing import Any, cast` and `# type: ignore[...]` as much as possible. If you work in a code base with little to no external libraries, then in **most** cases all typing problems are the outcome of bad code design.

All examples were prepared using python 3.11 and mypy 1.11.2 (if you have some troubles with reproduction). Python 3.12 makes some significant changes to the typing interface, however `mypy` compiler does not support it right now. This will be addressed after the release.

## Table of contents

- [The benefits of statically typed code](#the-benefits-of-statically-typed-code)
    - [Dealing with args and kwargs with `Unpack`](#dealing-with-args-and-kwargs-with-unpack)
    - [The lack of value and `Optional`](#the-lack-of-value-and-optional)
    - [What in case of no return... or `NoReturn`?](#what-in-case-of-no-return-or-noreturn)
    - [Difference between `TypeAlias` and `NewType`](#difference-between-typealias-and-newtype)
    - [Unnecessary imports with `TYPE_CHECKING` and forward declarations](#unnecessary-imports-with-type_checking-and-forward-declarations)
    - [Type narrowing with `TypeGuard`](#type-narrowing-with-typeguard)
    - [Inheritance with `final` and `override`](#inheritance-with-final-and-override)
    - [We have templates at home with `Generic` and `TypeVar`](#we-have-templates-at-home-with-generic-and-typevar)
    - [We have traits at home with `Protocol`](#we-have-traits-at-home-with-protocol)
    - [Dealing with callables and callback protocols](#dealing-with-callables-and-callback-protocols)
    - [Dealing with decorators](#dealing-with-decorators)
    - [Signature `overload`](#signature-overload)
    - [Dealing with mixins that access state](#dealing-with-mixins-that-access-state)
- [More extensive examples](#more-extensive-examples)

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

If our interface does not return a value (a `void` function in a sense) then a pythonic way is to type it with `None` return value:

```python
def test_function() -> None:
    return
```

However sometimes we can encounter functions which really do not return (by always raising an exception). A correct type:

```python
from typing import NoReturn

def test_function() -> NoReturn:
    raise ValueError
```

This way `mypy` will understand that code called after our function, is actually unreachable.

### Difference between `TypeAlias` and `NewType`

### Unnecessary imports with `TYPE_CHECKING` and forward declarations

If our module does not explicitely use a value in runtime, but we need it for a correct type annotation, we can actually avoid importing it in rutime (for performance reasons for example). A way to achieve that is to use the `TYPE_CHECKING` flag. It is set to `True` during the check, but always `False` in runtime.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # This won't be imported in runtime.
    from .expensive_module import Type

def test_function(value: Type) -> None:
    ...
```

It is important to note, that when importing types under the `TYPE_CHECKING` flag, we have to forward declare the types. We can do that either by annotating the type with a string:

```python
def test_function(value: "Type") -> None:
    ...
```

Or by utilizing the `__future__` module, to automatically replace all types with their forward declarations:

```python
from __future__ import annotations

def test_function(value: Type) -> None:
    ...
```

We can also use forward declarations to use not yet defined type to annotate something. For example:

```python
from __future__ import annotations

# this type is not yet defined, but we can annotate with forward
# declared type.
def test_function(value: SomeValue) -> None:
    ...

class SomeValue:
    ...
```

### Type narrowing with `TypeGuard`

One of the most useful features of any type compiler is the support for type narrowing. We actually did it before... let's see it again:

```python
def test_function(value: Optional[int]) -> None:
    if value is None:
        # Here mypy will understand that our value will always be None.
    else:
        # And here our value will always be an integer.
```

This is actually something we call a `TypeGuard`, we can narrow the type, by performing a runtime check. Python gives us multiple types of built in guards:

```python
def test_function(value: str | int) -> None:
    if isinstance(value, str):
        # Here we know our value is a string.
    else:
        # And here it will always be an integer.
```

But we can actually define custom guards:

```python
from typing import TypeGuard

def all_strings(values: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(value, str) for value in values)

values = ["1", "2"]

if all_strings(values):
    # In this scope we are sure values are strings, and our type checker
    # understands it as well.
```

A custom `TypeGuard` has to return a boolean, and take the checked value as the first argument, for the compiler to work correctly.

### Inheritance with `final` and `override`

Sometimes in our framework we want to create some internal types that are not meant to be inherited from. We can actually enforce that with the `final` decorator:

```python
from typing import final

@final
class MyType:
    ...
```

This type will now end the inheritance tree. Sometimes we want to stop the user from overriding only one method of our type. In this case we can decorate the method itself:

```python
from typing import final

class MyType:
    @final
    def dont_override_me(self) -> None:
        ...
```

In a deep inheritance tree it is sometimes hard to see which methods are overriden, which are new in our type. We can make everything more readable by using the `override` decorator (hello java enjoyers).

```python
from abc import ABC, abstractmethod
from typing_extensions import override
from typing import final

class Base(ABC):
    @abstractmethod
    def interface_method(self) -> None:
        raise NotImplementedError

@final
class Child(Base):
    @override
    def interface_method(self) -> None:
        ...
```

It is not only a clean-code thing, with the `override` and `final` decorators `mypy` will detect if our inheritance tree ended with some abstract interface still missing. We don't have to check it in runtime.

### We have templates at home (with `Generic` and `TypeVar`)

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Vector(Generic[T]):
    def __init__(self, initial: list[T]) -> None:
        self._values: list[T] = initial

vector = Vector[int](initial=[1, 2, 3])
```

```python
from abc import ABC, abstractmethod
from typing_extensions import override
from typing import Generic, TypeVar


T = TypeVar("T")

class BaseStorage(ABC, Generic[T]):
    def __init__(self) -> None:
        self._storage: list[T] = []

    @abstractmethod
    def add_item(self, item: T) -> None:
        raise NotImplementedError

class IntegerStorage(BaseStorage[int]):
    @override
    def add_item(self, item: int) -> None:
        self._storage.append(item)
```

```python
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class CustomDict(Generic[K, V]):
    def __init__(self) -> None:
        self._storage: dict[K, V] = {}
```

```python
from typing import TypeVar

Number = TypeVar("Number", int, float)
```

```python
from pydantic import BaseModel
from typing import TypeVar

Model = TypeVar("Model", bound=BaseModel)
```

### We have traits at home (with `Protocol`)

### Dealing with callables and callback protocols

### Dealing with decorators

One of the most popular design patterns in python is a humble decorator. In older python version however, static types for decorators were really bad. Thankfully now, we have a parameter specification variable `ParamSpec`, which allows us to inherit a type signature of other callable:

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

@log_return_value
def test_function(x: int) -> None:
    ...
```

This way, we inherit a generic return value of our callable and its arguments. When checking the signature of our decorated `test_function` it will be exactly the same as before the decorator was applied. Sometimes we need to specify an exact argument we will be accessing in the decorated function signature. We can achieve that by using the `Concatenate` type:

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

This way we enforce that this decorator will be used on `SomeClass` methods.

### Signature `overload`

Sometimes we want to define multiple ways to call our interface, especially when some argument types modify the returned value or the interface behaviour. We can do that using the `overload` decorator:

```python
from typing import overload, Sequence

@overload
def multiply(item: int, value: int) -> int: ...
@overload
def multiply(item: Sequence[int], value: int) -> Sequence[int]: ...

def multiply(item: int | Sequence[int], value: int) -> int | Sequence[int]:
    if isinstance(item, int):
        return item * value

    return [i * value for i in item]
```

You can additionally define some completly optional arguments for your interface:

```python
from pathlib import Path
from typing import Final, Literal, Optional, overload

BASE_PATH: Final = Path("/srv/")

@overload
def get_file_content(path: Literal[None] = None, file_name: str = ...) -> bytes: ...
@overload
def get_file_content(path: Path, file_name: Literal[None] = None) -> bytes: ...

def get_file_content(path: Optional[Path] = None, file_name: Optional[str] = None) -> bytes:
    if file_name:
        return (BASE_PATH / file_name).read_bytes()

    if path:
        return path.read_bytes()

    raise ValueError
```

### Dealing with mixins that access state

## More extensive examples

More examples which require more code, can be found in the `typing_examples/` directory.

- `typing_examples/circular_imports/`
- `typing_examples/type_narrowing_generic_result.py`
- `typing_examples/annotated.py`
