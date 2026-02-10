"""Interactive CLI agent for restaurant booking with Hebrew natural language parsing."""

import re
import sys
from typing import Optional

from .booking_engine import BookingEngine
from .models import Cuisine, Restaurant


# Mapping Hebrew/English keywords to cuisine types
CUISINE_KEYWORDS: dict[str, str] = {}
for c in Cuisine:
    CUISINE_KEYWORDS[c.value] = c.value
    CUISINE_KEYWORDS[c.name.lower()] = c.value

# Additional common keywords
CUISINE_KEYWORDS.update({
    "פיצה": "איטלקי", "פסטה": "איטלקי", "איטלקית": "איטלקי",
    "סושי": "יפני", "יפנית": "יפני", "ראמן": "יפני",
    "בורגר": "אמריקאי", "המבורגר": "אמריקאי", "אמריקאית": "אמריקאי",
    "צרפתית": "צרפתי", "קרואסון": "צרפתי",
    "מקסיקנית": "מקסיקני", "טאקו": "מקסיקני", "בוריטו": "מקסיקני",
    "ישראלית": "ישראלי", "חומוס": "ישראלי", "פלאפל": "ישראלי",
    "אסייתית": "אסייתי", "תאילנדי": "אסייתי", "סיני": "אסייתי",
    "ים תיכונית": "ים תיכוני",
})

CITY_KEYWORDS = ["תל אביב", "ירושלים", "חיפה"]

PRICE_KEYWORDS = {
    "זול": "₪", "זולה": "₪", "בזול": "₪",
    "בינוני": "₪₪", "בינונית": "₪₪", "סביר": "₪₪",
    "יקר": "₪₪₪", "יקרה": "₪₪₪",
    "יוקרתי": "₪₪₪₪", "יוקרתית": "₪₪₪₪", "פרימיום": "₪₪₪₪",
}

HELP_TEXT = """
╔══════════════════════════════════════════════════════════╗
║           סוכן הזמנת מסעדות - עזרה                      ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  פקודות זמינות:                                          ║
║                                                          ║
║  חפש / חיפוש    - חיפוש מסעדות                           ║
║    דוגמאות:                                              ║
║    • "חפש איטלקי בתל אביב"                               ║
║    • "מסעדה יפנית יוקרתית"                                ║
║    • "חפש מסעדות בירושלים"                                ║
║                                                          ║
║  הזמן            - הזמנת מקום                            ║
║    דוגמה: "הזמן 1 ל-15/03/2026 בשעה 20:00 ל-4 סועדים"  ║
║                                                          ║
║  בטל             - ביטול הזמנה                            ║
║    דוגמה: "בטל a1b2c3d4"                                 ║
║                                                          ║
║  הזמנות שלי      - צפייה בהזמנות קיימות                   ║
║    דוגמה: "הזמנות שלי 050-1234567"                       ║
║                                                          ║
║  מטבחים          - רשימת סוגי מטבח                        ║
║  ערים             - רשימת ערים זמינות                     ║
║  עזרה            - הצגת תפריט עזרה                        ║
║  יציאה           - יציאה מהסוכן                           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

WELCOME_TEXT = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         ברוכים הבאים לסוכן הזמנת המסעדות!               ║
║                                                          ║
║    אני כאן כדי לעזור לכם למצוא מסעדה ולהזמין מקום.      ║
║    הקלידו 'עזרה' לרשימת הפקודות הזמינות.                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""


class BookingAgent:
    """Interactive agent that parses Hebrew user input and manages the booking flow."""

    def __init__(self, engine: Optional[BookingEngine] = None) -> None:
        self.engine = engine or BookingEngine()
        self.last_search_results: list[Restaurant] = []

    def parse_and_execute(self, user_input: str) -> str:
        text = user_input.strip()
        if not text:
            return "לא הבנתי. הקלידו 'עזרה' לרשימת הפקודות."

        lower = text.lower()

        # Help
        if any(w in text for w in ["עזרה", "help"]):
            return HELP_TEXT

        # List cuisines
        if any(w in text for w in ["מטבחים", "סוגי מטבח", "קטגוריות"]):
            return self.engine.list_cuisines().message

        # List cities
        if any(w in text for w in ["ערים", "עיר", "איפה"]):
            return self.engine.list_cities().message

        # My reservations
        if "הזמנות שלי" in text or "ההזמנות שלי" in text:
            phone = self._extract_phone(text)
            if not phone:
                return "נא לציין מספר טלפון. דוגמה: 'הזמנות שלי 050-1234567'"
            return self.engine.my_reservations(phone).message

        # Cancel reservation
        if any(w in text for w in ["בטל", "ביטול", "cancel"]):
            return self._handle_cancel(text)

        # Make reservation
        if any(w in text for w in ["הזמן", "הזמנה", "reserve", "book"]):
            return self._handle_reservation(text)

        # Search (explicit or implicit)
        if any(w in text for w in ["חפש", "חיפוש", "מצא", "search", "מסעדה", "מסעדות"]):
            return self._handle_search(text)

        # Implicit search: check if input contains cuisine/city keywords
        cuisine = self._extract_cuisine(text)
        city = self._extract_city(text)
        if cuisine or city:
            return self._handle_search(text)

        return "לא הבנתי את הבקשה. הקלידו 'עזרה' לרשימת הפקודות הזמינות."

    def _handle_search(self, text: str) -> str:
        cuisine = self._extract_cuisine(text)
        city = self._extract_city(text)
        price = self._extract_price(text)
        rating = self._extract_min_rating(text)

        # If explicit search keyword used but no filters matched, try using
        # remaining words as a cuisine query so unrecognized terms return no results.
        if not any([cuisine, city, price, rating]):
            search_keywords = {"חפש", "חיפוש", "מצא", "search", "מסעדה", "מסעדות"}
            remaining = " ".join(w for w in text.split() if w not in search_keywords).strip()
            if remaining:
                cuisine = remaining

        response = self.engine.search(cuisine=cuisine, city=city, price_range=price, min_rating=rating)
        if response.restaurants:
            self.last_search_results = response.restaurants
        return response.message

    def _handle_reservation(self, text: str) -> str:
        # Try to parse: "הזמן <number> ל-<date> בשעה <time> ל-<party_size> סועדים"
        restaurant_idx = self._extract_restaurant_index(text)
        date = self._extract_date(text)
        time_slot = self._extract_time(text)
        party_size = self._extract_party_size(text)

        if restaurant_idx is None or not self.last_search_results:
            return (
                "נא לציין מספר מסעדה מתוצאות החיפוש האחרון.\n"
                "דוגמה: 'הזמן 1 ל-15/03/2026 בשעה 20:00 ל-4 סועדים'"
            )

        if restaurant_idx < 1 or restaurant_idx > len(self.last_search_results):
            return f"מספר מסעדה לא תקין. בחרו מספר בין 1 ל-{len(self.last_search_results)}."

        if not date:
            return "נא לציין תאריך. דוגמה: '15/03/2026'"
        if not time_slot:
            return "נא לציין שעה. דוגמה: '20:00'"
        if not party_size:
            return "נא לציין מספר סועדים. דוגמה: 'ל-4 סועדים'"

        restaurant = self.last_search_results[restaurant_idx - 1]

        # Ask for customer details
        return self._reservation_flow(restaurant.id, date, time_slot, party_size)

    def _reservation_flow(
        self, restaurant_id: str, date: str, time_slot: str, party_size: int
    ) -> str:
        # In interactive mode, we'll collect name and phone
        # For non-interactive/testing, this will be handled by the run loop
        self._pending_reservation = {
            "restaurant_id": restaurant_id,
            "date": date,
            "time": time_slot,
            "party_size": party_size,
        }
        return "NEED_CUSTOMER_INFO"

    def complete_reservation(self, name: str, phone: str) -> str:
        if not hasattr(self, "_pending_reservation") or not self._pending_reservation:
            return "אין הזמנה ממתינה."
        info = self._pending_reservation
        self._pending_reservation = None
        response = self.engine.make_reservation(
            restaurant_id=info["restaurant_id"],
            customer_name=name,
            customer_phone=phone,
            date=info["date"],
            time_slot=info["time"],
            party_size=info["party_size"],
        )
        return response.message

    def _handle_cancel(self, text: str) -> str:
        # Extract reservation ID (8 hex chars)
        match = re.search(r"[0-9a-f]{8}", text.lower())
        if not match:
            return "נא לציין מספר הזמנה. דוגמה: 'בטל a1b2c3d4'"
        return self.engine.cancel_reservation(match.group()).message

    def _extract_cuisine(self, text: str) -> Optional[str]:
        for keyword, cuisine in CUISINE_KEYWORDS.items():
            if keyword in text:
                return cuisine
        return None

    def _extract_city(self, text: str) -> Optional[str]:
        for city in CITY_KEYWORDS:
            if city in text:
                return city
        return None

    def _extract_price(self, text: str) -> Optional[str]:
        for keyword, price in PRICE_KEYWORDS.items():
            if keyword in text:
                return price
        return None

    def _extract_min_rating(self, text: str) -> Optional[float]:
        match = re.search(r"דירוג\s*(?:מעל|מינימום|לפחות)?\s*(\d+\.?\d*)", text)
        if match:
            return float(match.group(1))
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        match = re.search(r"(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})", text)
        if match:
            return match.group(1)
        return None

    def _extract_time(self, text: str) -> Optional[str]:
        match = re.search(r"(\d{1,2}:\d{2})", text)
        if match:
            return match.group(1)
        return None

    def _extract_party_size(self, text: str) -> Optional[int]:
        # "ל-4 סועדים" or "4 אנשים" or "4 סועדים"
        match = re.search(r"ל?-?(\d+)\s*(?:סועדים|אנשים|אורחים|מקומות)", text)
        if match:
            return int(match.group(1))
        return None

    def _extract_restaurant_index(self, text: str) -> Optional[int]:
        # "הזמן 1" or "הזמן מספר 3"
        match = re.search(r"(?:הזמן|הזמנה)\s*(?:מספר\s*)?(\d+)", text)
        if match:
            return int(match.group(1))
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        match = re.search(r"(0\d{1,2}-?\d{7,8})", text)
        if match:
            return match.group(1)
        return None


def main() -> None:
    """Run the interactive booking agent CLI."""
    agent = BookingAgent()
    print(WELCOME_TEXT)

    while True:
        try:
            user_input = input("\n🍽️  מה תרצו לעשות? > ")
        except (EOFError, KeyboardInterrupt):
            print("\n\nלהתראות! 👋")
            break

        lower = user_input.strip().lower()
        if lower in ["יציאה", "exit", "quit", "צא", "ביי"]:
            print("\nתודה שהשתמשתם בסוכן ההזמנות! להתראות! 👋")
            break

        response = agent.parse_and_execute(user_input)

        if response == "NEED_CUSTOMER_INFO":
            try:
                print("\nנא להזין פרטים להשלמת ההזמנה:")
                name = input("  שם מלא: ")
                phone = input("  מספר טלפון: ")
                if not name.strip() or not phone.strip():
                    print("הפרטים לא תקינים. ההזמנה בוטלה.")
                    agent._pending_reservation = None
                    continue
                response = agent.complete_reservation(name.strip(), phone.strip())
            except (EOFError, KeyboardInterrupt):
                print("\nההזמנה בוטלה.")
                agent._pending_reservation = None
                continue

        print(f"\n{response}")


if __name__ == "__main__":
    main()
