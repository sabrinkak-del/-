"""Preview/demo script - runs the booking agent with predefined inputs to showcase features."""

import time as time_module
from restaurant_booking.agent import BookingAgent, WELCOME_TEXT


DEMO_STEPS = [
    ("ערים", "צפייה ברשימת ערים זמינות"),
    ("מטבחים", "צפייה בסוגי מטבח"),
    ("חפש סושי בתל אביב", "חיפוש מסעדת סושי בתל אביב"),
    ("הזמן 1 ל-20/03/2026 בשעה 20:00 ל-2 סועדים", "הזמנת מקום במסעדה"),
    ("הזמנות שלי 050-1234567", "צפייה בהזמנות"),
    ("חפש ישראלי בחיפה", "חיפוש מסעדה ישראלית בחיפה"),
    ("חפש מסעדה יוקרתית", "חיפוש מסעדה יוקרתית"),
]

SEPARATOR = "\n" + "─" * 60 + "\n"


def print_slow(text: str, delay: float = 0.01) -> None:
    for char in text:
        print(char, end="", flush=True)
        time_module.sleep(delay)
    print()


def main() -> None:
    agent = BookingAgent()

    print(WELCOME_TEXT)
    print_slow("    מצב הדגמה - Preview Mode")
    print(SEPARATOR)

    for i, (command, description) in enumerate(DEMO_STEPS, 1):
        print(f"  [{i}/{len(DEMO_STEPS)}] {description}")
        print(f"  > {command}")
        print()

        response = agent.parse_and_execute(command)

        # Handle reservation flow with demo customer info
        if response == "NEED_CUSTOMER_INFO":
            print("  (מזין פרטי לקוח: דני כהן, 050-1234567)")
            print()
            response = agent.complete_reservation("דני כהן", "050-1234567")

        print(response)
        print(SEPARATOR)

        time_module.sleep(0.5)

    print_slow("  ההדגמה הסתיימה! להפעלה אינטראקטיבית:")
    print_slow("  python -m restaurant_booking")
    print()


if __name__ == "__main__":
    main()
