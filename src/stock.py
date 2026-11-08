import json
from dataclasses import dataclass
from pathlib import Path

IN_STOCK = "in_stock"
OUT_OF_STOCK = "out_of_stock"
UNKNOWN = "unknown"
AVAILABILITIES = (IN_STOCK, OUT_OF_STOCK, UNKNOWN)


@dataclass(frozen=True)
class Retailer:
    name: str
    variant: str
    availability: str
    order_url: str
    host: str

    @classmethod
    def from_dict(cls, d):
        r = cls(d["name"], d["variant"], d["availability"], d["order_url"], d["host"])
        for field in (r.name, r.variant):
            if not isinstance(field, str) or not field.strip():
                raise ValueError(f"name and variant must be non-empty text: {d!r}")
        if r.availability not in AVAILABILITIES:
            raise ValueError(f"{r.name}: unknown availability {r.availability!r}")
        return r


def load_retailers(path):
    return [Retailer.from_dict(d) for d in json.loads(Path(path).read_text())["retailers"]]
