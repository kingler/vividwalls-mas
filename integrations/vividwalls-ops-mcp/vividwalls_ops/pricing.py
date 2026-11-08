"""Pricing rule: retail = Pictorem pro cost x 2.065, never below 1.8x cost without approval."""
from . import config


def retail_price(pictorem_cost: float) -> float:
    return round(pictorem_cost * config.MARKUP, 2)


def implied_cost(retail: float) -> float:
    return round(retail / config.MARKUP, 2)


def check_price(retail: float, pictorem_cost: float) -> dict:
    """Says whether a proposed retail price respects the floor, and its margin."""
    multiple = retail / pictorem_cost if pictorem_cost else 0.0
    return {
        "retail": round(retail, 2),
        "pictorem_cost": round(pictorem_cost, 2),
        "multiple": round(multiple, 3),
        "gross_margin_pct": round((1 - pictorem_cost / retail) * 100, 1) if retail else 0.0,
        "meets_floor": multiple >= config.PRICE_FLOOR_MULTIPLE,
        "standard_price": retail_price(pictorem_cost),
    }
