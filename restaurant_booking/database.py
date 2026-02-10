"""Sample restaurant database and data access layer."""

from datetime import time
from typing import Optional

from .models import Cuisine, PriceRange, Restaurant, Reservation, ReservationStatus, generate_id


RESTAURANTS: list[Restaurant] = [
    Restaurant(
        id="r1", name="לה פיאצה", cuisine=Cuisine.ITALIAN,
        city="תל אביב", address="רחוב דיזנגוף 99",
        price_range=PriceRange.HIGH, rating=4.7, total_seats=60,
        opening_time=time(12, 0), closing_time=time(23, 0),
        phone="03-1234567",
    ),
    Restaurant(
        id="r2", name="סאקורה", cuisine=Cuisine.JAPANESE,
        city="תל אביב", address="רחוב בן יהודה 45",
        price_range=PriceRange.PREMIUM, rating=4.9, total_seats=40,
        opening_time=time(18, 0), closing_time=time(23, 30),
        phone="03-2345678",
    ),
    Restaurant(
        id="r3", name="טאקו לוקו", cuisine=Cuisine.MEXICAN,
        city="ירושלים", address="רחוב יפו 22",
        price_range=PriceRange.LOW, rating=4.3, total_seats=45,
        opening_time=time(11, 0), closing_time=time(23, 0),
        phone="02-3456789",
    ),
    Restaurant(
        id="r4", name="ביסטרו פריז", cuisine=Cuisine.FRENCH,
        city="חיפה", address="שדרות הנשיא 15",
        price_range=PriceRange.PREMIUM, rating=4.8, total_seats=35,
        opening_time=time(18, 0), closing_time=time(0, 0),
        phone="04-4567890",
    ),
    Restaurant(
        id="r5", name="שולחן ערוך", cuisine=Cuisine.ISRAELI,
        city="תל אביב", address="שוק הכרמל 7",
        price_range=PriceRange.MEDIUM, rating=4.5, total_seats=70,
        opening_time=time(8, 0), closing_time=time(22, 0),
        phone="03-5678901",
    ),
    Restaurant(
        id="r6", name="באנג בנגקוק", cuisine=Cuisine.ASIAN,
        city="ירושלים", address="רחוב אגריפס 30",
        price_range=PriceRange.MEDIUM, rating=4.4, total_seats=50,
        opening_time=time(12, 0), closing_time=time(23, 0),
        phone="02-6789012",
    ),
    Restaurant(
        id="r7", name="המטבח של אמא", cuisine=Cuisine.ISRAELI,
        city="חיפה", address="רחוב הרצל 55",
        price_range=PriceRange.LOW, rating=4.6, total_seats=80,
        opening_time=time(7, 0), closing_time=time(22, 0),
        phone="04-7890123",
    ),
    Restaurant(
        id="r8", name="ברגר סטיישן", cuisine=Cuisine.AMERICAN,
        city="תל אביב", address="רחוב אלנבי 78",
        price_range=PriceRange.LOW, rating=4.2, total_seats=55,
        opening_time=time(11, 0), closing_time=time(1, 0),
        phone="03-8901234",
    ),
    Restaurant(
        id="r9", name="יאמה", cuisine=Cuisine.MEDITERRANEAN,
        city="ירושלים", address="רחוב שלומציון 12",
        price_range=PriceRange.HIGH, rating=4.6, total_seats=45,
        opening_time=time(12, 0), closing_time=time(23, 0),
        phone="02-9012345",
    ),
    Restaurant(
        id="r10", name="טוקיו גריל", cuisine=Cuisine.JAPANESE,
        city="חיפה", address="שדרות בן גוריון 33",
        price_range=PriceRange.HIGH, rating=4.5, total_seats=38,
        opening_time=time(17, 0), closing_time=time(23, 0),
        phone="04-0123456",
    ),
]


class BookingDatabase:
    """In-memory database for restaurants and reservations."""

    def __init__(self) -> None:
        self.restaurants: dict[str, Restaurant] = {r.id: r for r in RESTAURANTS}
        self.reservations: dict[str, Reservation] = {}

    def get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        return self.restaurants.get(restaurant_id)

    def search_restaurants(
        self,
        cuisine: Optional[str] = None,
        city: Optional[str] = None,
        price_range: Optional[str] = None,
        min_rating: Optional[float] = None,
    ) -> list[Restaurant]:
        results = list(self.restaurants.values())

        if cuisine:
            results = [
                r for r in results
                if cuisine in r.cuisine.value or cuisine.lower() in r.cuisine.name.lower()
            ]
        if city:
            results = [r for r in results if city in r.city]
        if price_range:
            results = [r for r in results if price_range == r.price_range.value]
        if min_rating is not None:
            results = [r for r in results if r.rating >= min_rating]

        return sorted(results, key=lambda r: r.rating, reverse=True)

    def get_available_seats(self, restaurant_id: str, date: str, time_slot: str) -> int:
        restaurant = self.get_restaurant(restaurant_id)
        if not restaurant:
            return 0

        booked = sum(
            r.party_size
            for r in self.reservations.values()
            if r.restaurant_id == restaurant_id
            and r.date == date
            and r.time == time_slot
            and r.status == ReservationStatus.CONFIRMED
        )
        return max(0, restaurant.total_seats - booked)

    def create_reservation(
        self,
        restaurant_id: str,
        customer_name: str,
        customer_phone: str,
        date: str,
        time_slot: str,
        party_size: int,
    ) -> Optional[Reservation]:
        available = self.get_available_seats(restaurant_id, date, time_slot)
        if available < party_size:
            return None

        reservation = Reservation(
            id=generate_id(),
            restaurant_id=restaurant_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            date=date,
            time=time_slot,
            party_size=party_size,
        )
        self.reservations[reservation.id] = reservation
        return reservation

    def cancel_reservation(self, reservation_id: str) -> bool:
        reservation = self.reservations.get(reservation_id)
        if not reservation or reservation.status == ReservationStatus.CANCELLED:
            return False
        reservation.status = ReservationStatus.CANCELLED
        return True

    def get_reservations_by_phone(self, phone: str) -> list[Reservation]:
        return [
            r for r in self.reservations.values()
            if r.customer_phone == phone and r.status == ReservationStatus.CONFIRMED
        ]

    def get_reservation_by_id(self, reservation_id: str) -> Optional[Reservation]:
        return self.reservations.get(reservation_id)
