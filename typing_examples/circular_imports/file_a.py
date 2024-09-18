from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from file_b import B


class A:
    @classmethod
    def from_b(cls, b: B) -> Self:
        return cls()
