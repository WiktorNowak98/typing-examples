from dataclasses import dataclass
from typing import Literal, Optional, Protocol, TypeVar

T = TypeVar("T")


class ResultInterface(Protocol[T]):
    response: Optional[T]
    error: Optional[BaseException]
    is_success: bool


@dataclass
class Ok(ResultInterface[T]):
    response: T
    error: Literal[None] = None
    is_success: Literal[True] = True


@dataclass
class Err(ResultInterface[T]):
    error: BaseException
    response: Literal[None] = None
    is_success: Literal[False] = False


def interface(value: int) -> Ok[int] | Err[int]:
    return Ok(response=value) if value > 10 else Err(error=ValueError())


result = interface(12)

if result.is_success is True:
    # Because our result class has well defined type interface, we can
    # narrow the type by performing the simple of the member.
    result.response
else:
    result.error
