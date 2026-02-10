"""Tests for data models."""

from datetime import time

from restaurant_booking.models import (
    Cuisine,
    PriceRange,
    ReservationStatus,
    Restaurant,
    Reservation,
    generate_id,
)


def test_generate_id_is_unique():
    ids = {generate_id() for _ in range(100)}
    assert len(ids) == 100


def test_restaurant_str():
    r = Restaurant(
        id="test",
        name="טסט",
        cuisine=Cuisine.ITALIAN,
        city="תל אביב",
        address="רחוב 1",
        price_range=PriceRange.HIGH,
        rating=4.5,
        total_seats=50,
        opening_time=time(12, 0),
        closing_time=time(23, 0),
        phone="03-1234567",
    )
    s = str(r)
    assert "טסט" in s
    assert "איטלקי" in s
    assert "4.5" in s


def test_reservation_str():
    r = Reservation(
        id="abcdef12-3456-7890-abcd-ef1234567890",
        restaurant_id="r1",
        customer_name="ישראל ישראלי",
        customer_phone="050-1234567",
        date="15/03/2026",
        time="20:00",
        party_size=4,
    )
    s = str(r)
    assert "abcdef12" in s
    assert "ישראל ישראלי" in s
    assert "4 סועדים" in s
    assert "מאושר" in s


def test_reservation_status_values():
    assert ReservationStatus.CONFIRMED.value == "מאושר"
    assert ReservationStatus.CANCELLED.value == "מבוטל"
