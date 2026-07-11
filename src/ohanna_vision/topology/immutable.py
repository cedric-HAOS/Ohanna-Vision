"""Utilities for immutable topology domain values."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any


def freeze_value(value: Any) -> Any:
    """Recursively convert a value into an immutable representation."""
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                key: freeze_value(nested_value)
                for key, nested_value in value.items()
            }
        )

    if isinstance(value, list | tuple):
        return tuple(
            freeze_value(item)
            for item in value
        )

    if isinstance(value, set | frozenset):
        return frozenset(
            freeze_value(item)
            for item in value
        )

    return value


def freeze_mapping(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    """Return a deeply immutable copy of a metadata mapping."""
    frozen = freeze_value(value)

    if not isinstance(frozen, Mapping):
        raise TypeError("frozen value must remain a mapping")

    return frozen