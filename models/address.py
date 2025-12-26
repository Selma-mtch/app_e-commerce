from dataclasses import dataclass


@dataclass
class Address:
    id: str
    street: str
    line2: str
    postal_code: str
    city: str
    country: str = "France"
