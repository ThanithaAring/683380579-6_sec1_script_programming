# agentic-web-scraper/src/data_models.py
"""Data models for scraped entities."""

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Product:
    """Data model for a scraped product."""

    name: str
    price: str
    description: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self):
        """Convert the Product to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """Create a Product from a dictionary."""
        return cls(**data)
