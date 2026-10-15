"""
Map raw model labels (e.g. ImageNet class names) to our normalized
waste categories.

Design:
- Keyword-based matching, case-insensitive.
- Longest/most-specific keyword wins (checked first).
- Deterministic: same label always maps to the same category.
- Fallback to WasteCategory.OTHER when nothing matches.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.classification import (
    CategoryInfo,
    Recyclability,
    WasteCategory,
)


@dataclass(frozen=True)
class _CategoryRule:
    category: WasteCategory
    keywords: tuple[str, ...]
    display_name: str
    recyclability: Recyclability
    short_advice: str


# Rules are checked in order — more specific categories first.
# Each keyword is matched as a substring of the lowercased label.
_RULES: tuple[_CategoryRule, ...] = (
    _CategoryRule(
        category=WasteCategory.BATTERY,
        keywords=(
            "battery", "batteries", "accumulator", "cell", "power bank",
        ),
        display_name="Battery",
        recyclability=Recyclability.CONDITIONAL,
        short_advice=(
            "Take to a battery drop-off point. Never place in general or "
            "recycling bins — fire and chemical leak risk."
        ),
    ),
    _CategoryRule(
        category=WasteCategory.HAZARDOUS,
        keywords=(
            "syringe", "needle", "medical", "aerosol", "paint", "solvent",
            "pesticide", "insecticide", "thermometer", "mercury", "asbestos",
            "electronic", "e-waste", "circuit", "motherboard", "crt", "bulb",
            "fluorescent", "lamp",
        ),
        display_name="Hazardous waste",
        recyclability=Recyclability.NOT_RECYCLABLE,
        short_advice=(
            "Handle with care. Use your local hazardous waste facility — "
            "never mix with household recycling."
        ),
    ),
    _CategoryRule(
        category=WasteCategory.CHEMICAL,
        keywords=(
            "chemical", "detergent", "bleach", "cleaner", "acid", "alkali",
            "antifreeze", "motor oil", "oil can", "fuel", "gasoline", "diesel",
            "kerosene", "pesticide bottle",
        ),
        display_name="Chemical",
        recyclability=Recyclability.NOT_RECYCLABLE,
        short_advice=(
            "Keep sealed. Take to a household chemical disposal site. "
            "Do not pour down drains."
        ),
    ),
    _CategoryRule(
        category=WasteCategory.PLASTIC,
        keywords=(
            "plastic", "bottle", "water bottle", "soda bottle", "container",
            "bag", "packet", "wrapper", "straw", "cup", "yogurt", "tub",
            "bucket", "jug", "jerry can", "pet", "hdpe", "pvc", "polystyrene",
            "styrofoam", "bucket",
        ),
        display_name="Plastic",
        recyclability=Recyclability.CONDITIONAL,
        short_advice=(
            "Rinse and remove caps. Check the resin code — #1, #2, #5 are "
            "usually accepted; #3, #4, #6, #7 often are not."
        ),
    ),
    _CategoryRule(
        category=WasteCategory.PAPER,
        keywords=(
            "paper", "newspaper", "magazine", "book", "cardboard", "carton",
            "envelope", "notebook", "tissue", "receipt", "flyer", "brochure",
            "paperback",
        ),
        display_name="Paper",
        recyclability=Recyclability.RECYCLABLE,
        short_advice=(
            "Keep dry and clean. Flatten cardboard. Remove plastic tape and "
            "greasy food residue."
        ),
    ),
    _CategoryRule(
        category=WasteCategory.FABRIC,
        keywords=(
            "shirt", "t-shirt", "tshirt", "dress", "jeans", "trouser", "pant",
            "jacket", "coat", "sweater", "hoodie", "sock", "shoe", "sneaker",
            "boot", "hat", "cap", "scarf", "cloth", "textile", "fabric",
            "towel", "bedsheet", "curtain", "carpet",
        ),
        display_name="Fabric / textile",
        recyclability=Recyclability.CONDITIONAL,
        short_advice=(
            "Donate if wearable. Otherwise use textile recycling banks — "
            "do not place in general recycling."
        ),
    ),
    _CategoryRule(
        category=WasteCategory.BIODEGRADABLE,
        keywords=(
            "apple", "banana", "orange", "fruit", "vegetable", "food", "leaf",
            "leaves", "plant", "flower", "grass", "bread", "rice", "pasta",
            "coffee", "tea", "egg", "bone", "compost", "organic",
        ),
        display_name="Biodegradable / organic",
        recyclability=Recyclability.RECYCLABLE,
        short_advice=(
            "Compost at home or place in the organics bin. Avoid mixing with "
            "recyclables — contamination hurts whole batches."
        ),
    ),
)


def _build_category_info(rule: _CategoryRule) -> CategoryInfo:
    return CategoryInfo(
        category=rule.category,
        display_name=rule.display_name,
        recyclability=rule.recyclability,
        short_advice=rule.short_advice,
    )


_OTHER_INFO = CategoryInfo(
    category=WasteCategory.OTHER,
    display_name="Other / unknown",
    recyclability=Recyclability.UNKNOWN,
    short_advice=(
        "Category could not be determined confidently. When in doubt, place "
        "in general waste or ask your local recycling authority."
    ),
)


def map_label_to_category(label: str) -> CategoryInfo:
    """
    Map a raw model label to a normalized waste category.

    Returns CategoryInfo — falls back to 'other' when nothing matches.
    Never raises; always returns a category.
    """
    if not label or not isinstance(label, str):
        return _OTHER_INFO

    haystack = label.lower()

    for rule in _RULES:
        for keyword in rule.keywords:
            if keyword in haystack:
                return _build_category_info(rule)

    return _OTHER_INFO


def all_category_infos() -> list[CategoryInfo]:
    """Return one CategoryInfo per rule (useful for API metadata)."""
    infos = [_build_category_info(r) for r in _RULES]
    infos.append(_OTHER_INFO)
    return infos