"""Core booking engine that processes user intents and manages the booking flow."""

from dataclasses import dataclass
from typing import Optional

from .database import BookingDatabase
from .models import Cuisine, PriceRange, Restaurant, Reservation


@dataclass
class AgentResponse:
    message: str
    restaurants: Optional[list[Restaurant]] = None
    reservation: Optional[Reservation] = None


class BookingEngine:
    """Processes booking commands and returns structured responses."""

    def __init__(self, db: Optional[BookingDatabase] = None) -> None:
        self.db = db or BookingDatabase()

    def search(
        self,
        cuisine: Optional[str] = None,
        city: Optional[str] = None,
        price_range: Optional[str] = None,
        min_rating: Optional[float] = None,
    ) -> AgentResponse:
        results = self.db.search_restaurants(cuisine, city, price_range, min_rating)
        if not results:
            return AgentResponse(message="לא נמצאו מסעדות התואמות את החיפוש.")

        lines = ["מסעדות שנמצאו:", ""]
        for i, r in enumerate(results, 1):
            lines.append(
                f"  {i}. {r.name} | {r.cuisine.value} | {r.city} | "
                f"{r.price_range.value} | דירוג: {r.rating}/5"
            )
            lines.append(f"     כתובת: {r.address} | טלפון: {r.phone}")
            lines.append(f"     שעות פעילות: {r.opening_time.strftime('%H:%M')}-{r.closing_time.strftime('%H:%M')}")
            lines.append("")

        lines.append("כדי להזמין מקום, ציין את מספר המסעדה, תאריך, שעה ומספר סועדים.")
        return AgentResponse(message="\n".join(lines), restaurants=results)

    def check_availability(
        self, restaurant_id: str, date: str, time_slot: str
    ) -> AgentResponse:
        restaurant = self.db.get_restaurant(restaurant_id)
        if not restaurant:
            return AgentResponse(message="מסעדה לא נמצאה.")

        available = self.db.get_available_seats(restaurant_id, date, time_slot)
        return AgentResponse(
            message=f"ב{restaurant.name} בתאריך {date} בשעה {time_slot} "
                    f"יש {available} מקומות פנויים."
        )

    def make_reservation(
        self,
        restaurant_id: str,
        customer_name: str,
        customer_phone: str,
        date: str,
        time_slot: str,
        party_size: int,
    ) -> AgentResponse:
        restaurant = self.db.get_restaurant(restaurant_id)
        if not restaurant:
            return AgentResponse(message="מסעדה לא נמצאה.")

        reservation = self.db.create_reservation(
            restaurant_id, customer_name, customer_phone, date, time_slot, party_size
        )
        if not reservation:
            available = self.db.get_available_seats(restaurant_id, date, time_slot)
            return AgentResponse(
                message=f"מצטערים, אין מספיק מקומות פנויים ב{restaurant.name} "
                        f"בתאריך {date} בשעה {time_slot}. "
                        f"מקומות פנויים: {available}."
            )

        return AgentResponse(
            message=(
                f"ההזמנה אושרה!\n"
                f"  מסעדה: {restaurant.name}\n"
                f"  תאריך: {date}\n"
                f"  שעה: {time_slot}\n"
                f"  סועדים: {party_size}\n"
                f"  שם: {customer_name}\n"
                f"  טלפון: {customer_phone}\n"
                f"  מספר הזמנה: {reservation.id[:8]}\n\n"
                f"שמרו את מספר ההזמנה לביטול או שינוי."
            ),
            reservation=reservation,
        )

    def cancel_reservation(self, reservation_id: str) -> AgentResponse:
        # Support short IDs (first 8 chars)
        full_id = None
        for rid in self.db.reservations:
            if rid.startswith(reservation_id):
                full_id = rid
                break

        if not full_id:
            return AgentResponse(message="הזמנה לא נמצאה. בדקו את מספר ההזמנה.")

        reservation = self.db.get_reservation_by_id(full_id)
        restaurant = self.db.get_restaurant(reservation.restaurant_id)
        success = self.db.cancel_reservation(full_id)

        if not success:
            return AgentResponse(message="לא ניתן לבטל את ההזמנה. ייתכן שהיא כבר בוטלה.")

        return AgentResponse(
            message=f"ההזמנה ב{restaurant.name} בתאריך {reservation.date} "
                    f"בשעה {reservation.time} בוטלה בהצלחה."
        )

    def my_reservations(self, phone: str) -> AgentResponse:
        reservations = self.db.get_reservations_by_phone(phone)
        if not reservations:
            return AgentResponse(message="לא נמצאו הזמנות פעילות עבור מספר זה.")

        lines = ["ההזמנות שלך:", ""]
        for r in reservations:
            restaurant = self.db.get_restaurant(r.restaurant_id)
            name = restaurant.name if restaurant else "לא ידוע"
            lines.append(
                f"  • {name} | {r.date} {r.time} | "
                f"{r.party_size} סועדים | הזמנה: {r.id[:8]}"
            )
        return AgentResponse(message="\n".join(lines))

    def list_cuisines(self) -> AgentResponse:
        lines = ["סוגי מטבח זמינים:", ""]
        for c in Cuisine:
            lines.append(f"  • {c.value}")
        return AgentResponse(message="\n".join(lines))

    def list_cities(self) -> AgentResponse:
        cities = sorted(set(r.city for r in self.db.restaurants.values()))
        lines = ["ערים זמינות:", ""]
        for city in cities:
            count = sum(1 for r in self.db.restaurants.values() if r.city == city)
            lines.append(f"  • {city} ({count} מסעדות)")
        return AgentResponse(message="\n".join(lines))
