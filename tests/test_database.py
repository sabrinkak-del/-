"""Tests for the booking database."""

from restaurant_booking.database import BookingDatabase
from restaurant_booking.models import ReservationStatus


def make_db() -> BookingDatabase:
    return BookingDatabase()


def test_initial_restaurants():
    db = make_db()
    assert len(db.restaurants) == 10


def test_get_restaurant():
    db = make_db()
    r = db.get_restaurant("r1")
    assert r is not None
    assert r.name == "לה פיאצה"


def test_get_restaurant_not_found():
    db = make_db()
    assert db.get_restaurant("nonexistent") is None


def test_search_by_cuisine():
    db = make_db()
    results = db.search_restaurants(cuisine="יפני")
    assert len(results) == 2
    assert all(r.cuisine.value == "יפני" for r in results)


def test_search_by_city():
    db = make_db()
    results = db.search_restaurants(city="תל אביב")
    assert len(results) == 4


def test_search_by_price():
    db = make_db()
    results = db.search_restaurants(price_range="₪₪₪₪")
    assert len(results) == 2


def test_search_by_min_rating():
    db = make_db()
    results = db.search_restaurants(min_rating=4.7)
    assert all(r.rating >= 4.7 for r in results)


def test_search_combined():
    db = make_db()
    results = db.search_restaurants(cuisine="ישראלי", city="חיפה")
    assert len(results) == 1
    assert results[0].name == "המטבח של אמא"


def test_search_no_results():
    db = make_db()
    results = db.search_restaurants(cuisine="הודי")
    assert len(results) == 0


def test_create_reservation():
    db = make_db()
    r = db.create_reservation("r1", "ישראל", "050-1234567", "15/03/2026", "20:00", 4)
    assert r is not None
    assert r.customer_name == "ישראל"
    assert r.party_size == 4
    assert r.status == ReservationStatus.CONFIRMED


def test_create_reservation_no_space():
    db = make_db()
    # Fill up the restaurant (60 seats)
    db.create_reservation("r1", "א", "050-0000001", "15/03/2026", "20:00", 60)
    # Try to book more
    r = db.create_reservation("r1", "ב", "050-0000002", "15/03/2026", "20:00", 1)
    assert r is None


def test_available_seats():
    db = make_db()
    available = db.get_available_seats("r1", "15/03/2026", "20:00")
    assert available == 60  # full capacity

    db.create_reservation("r1", "א", "050-0000001", "15/03/2026", "20:00", 10)
    available = db.get_available_seats("r1", "15/03/2026", "20:00")
    assert available == 50


def test_cancel_reservation():
    db = make_db()
    r = db.create_reservation("r1", "ישראל", "050-1234567", "15/03/2026", "20:00", 4)
    assert db.cancel_reservation(r.id)
    assert r.status == ReservationStatus.CANCELLED


def test_cancel_already_cancelled():
    db = make_db()
    r = db.create_reservation("r1", "ישראל", "050-1234567", "15/03/2026", "20:00", 4)
    db.cancel_reservation(r.id)
    assert not db.cancel_reservation(r.id)


def test_cancel_nonexistent():
    db = make_db()
    assert not db.cancel_reservation("nonexistent")


def test_get_reservations_by_phone():
    db = make_db()
    db.create_reservation("r1", "ישראל", "050-1234567", "15/03/2026", "20:00", 4)
    db.create_reservation("r2", "ישראל", "050-1234567", "16/03/2026", "19:00", 2)
    db.create_reservation("r3", "אחר", "050-9999999", "15/03/2026", "20:00", 3)

    results = db.get_reservations_by_phone("050-1234567")
    assert len(results) == 2


def test_cancelled_not_in_active():
    db = make_db()
    r = db.create_reservation("r1", "ישראל", "050-1234567", "15/03/2026", "20:00", 4)
    db.cancel_reservation(r.id)
    results = db.get_reservations_by_phone("050-1234567")
    assert len(results) == 0


def test_cancelled_frees_seats():
    db = make_db()
    r = db.create_reservation("r1", "ישראל", "050-1234567", "15/03/2026", "20:00", 30)
    assert db.get_available_seats("r1", "15/03/2026", "20:00") == 30
    db.cancel_reservation(r.id)
    assert db.get_available_seats("r1", "15/03/2026", "20:00") == 60
