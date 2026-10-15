"""Unit tests for the waste-category mapper."""

import pytest

from app.schemas.classification import Recyclability, WasteCategory
from app.services.classification.category_mapper import (
    all_category_infos,
    map_label_to_category,
)


@pytest.mark.parametrize(
    "label, expected",
    [
        ("water bottle", WasteCategory.PLASTIC),
        ("plastic bag", WasteCategory.PLASTIC),
        ("newspaper", WasteCategory.PAPER),
        ("cardboard box", WasteCategory.PAPER),
        ("t-shirt", WasteCategory.FABRIC),
        ("running shoe", WasteCategory.FABRIC),
        ("AA battery", WasteCategory.BATTERY),
        ("lithium battery", WasteCategory.BATTERY),
        ("bleach bottle", WasteCategory.CHEMICAL),
        ("motor oil", WasteCategory.CHEMICAL),
        ("medical syringe", WasteCategory.HAZARDOUS),
        ("fluorescent lamp", WasteCategory.HAZARDOUS),
        ("banana peel", WasteCategory.BIODEGRADABLE),
        ("coffee grounds", WasteCategory.BIODEGRADABLE),
        ("xyz123 nonsense label", WasteCategory.OTHER),
        ("", WasteCategory.OTHER),
    ],
)
def test_map_label_to_category(label: str, expected: WasteCategory) -> None:
    info = map_label_to_category(label)
    assert info.category == expected, f"{label!r} -> {info.category} (expected {expected})"


def test_mapper_is_case_insensitive() -> None:
    assert map_label_to_category("WATER BOTTLE").category == WasteCategory.PLASTIC
    assert map_label_to_category("Newspaper").category == WasteCategory.PAPER


def test_mapper_never_raises_on_bad_input() -> None:
    # None and non-strings must return OTHER rather than raising
    assert map_label_to_category(None).category == WasteCategory.OTHER  # type: ignore[arg-type]
    assert map_label_to_category(123).category == WasteCategory.OTHER  # type: ignore[arg-type]


def test_mapper_returns_full_category_info() -> None:
    info = map_label_to_category("water bottle")
    assert info.display_name  # non-empty
    assert info.short_advice  # non-empty
    assert info.recyclability in {
        Recyclability.RECYCLABLE,
        Recyclability.CONDITIONAL,
        Recyclability.NOT_RECYCLABLE,
        Recyclability.UNKNOWN,
    }


def test_all_category_infos_covers_every_category() -> None:
    infos = all_category_infos()
    categories = {i.category for i in infos}
    # Every enum member must appear at least once
    for cat in WasteCategory:
        assert cat in categories, f"Missing category in all_category_infos(): {cat}"