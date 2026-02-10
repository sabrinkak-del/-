"""Data models for the restaurant booking system."""

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Optional
import uuid


class Cuisine(Enum):
    ITALIAN = "איטלקי"
    JAPANESE = "יפני"
    MEXICAN = "מקסיקני"
    FRENCH = "צרפתי"
    ISRAELI = "ישראלי"
    ASIAN = "אסייתי"
    AMERICAN = "אמריקאי"
    MEDITERRANEAN = "ים תיכוני"


class PriceRange(Enum):
    LOW = "₪"
    MEDIUM = "₪₪"
    HIGH = "₪₪₪"
    PREMIUM = "₪₪₪₪"


class ReservationStatus(Enum):
    CONFIRMED = "מאושר"
    CANCELLED = "מבוטל"


@dataclass
class Restaurant:
    id: str
    name: str
    cuisine: Cuisine
    city: str
    address: str
    price_range: PriceRange
    rating: float
    total_seats: int
    opening_time: time
    closing_time: time
    phone: str

    def __str__(self) -> str:
        return (
            f"{self.name} | {self.cuisine.value} | {self.city} | "
            f"{self.price_range.value} | דירוג: {self.rating}/5"
        )


@dataclass
class Reservation:
    id: str
    restaurant_id: str
    customer_name: str
    customer_phone: str
    date: str
    time: str
    party_size: int
    status: ReservationStatus = ReservationStatus.CONFIRMED

    def __str__(self) -> str:
        return (
            f"הזמנה #{self.id[:8]} | {self.customer_name} | "
            f"{self.date} {self.time} | {self.party_size} סועדים | "
            f"סטטוס: {self.status.value}"
        )


def generate_id() -> str:
    return str(uuid.uuid4())
