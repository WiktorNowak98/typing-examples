from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from file_a import A


class B:
    @classmethod
    def from_a(cls, a: A) -> Self:
        return cls()
