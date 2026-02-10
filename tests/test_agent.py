"""Tests for the booking agent's natural language parsing and flow."""

from restaurant_booking.agent import BookingAgent


def make_agent() -> BookingAgent:
    return BookingAgent()


def test_help():
    agent = make_agent()
    response = agent.parse_and_execute("עזרה")
    assert "פקודות זמינות" in response


def test_list_cuisines():
    agent = make_agent()
    response = agent.parse_and_execute("מטבחים")
    assert "איטלקי" in response
    assert "יפני" in response


def test_list_cities():
    agent = make_agent()
    response = agent.parse_and_execute("ערים")
    assert "תל אביב" in response
    assert "ירושלים" in response
    assert "חיפה" in response


def test_search_by_cuisine():
    agent = make_agent()
    response = agent.parse_and_execute("חפש מסעדה יפנית")
    assert "סאקורה" in response
    assert "טוקיו גריל" in response


def test_search_by_city():
    agent = make_agent()
    response = agent.parse_and_execute("חפש מסעדות בירושלים")
    assert "טאקו לוקו" in response
    assert "באנג בנגקוק" in response


def test_search_by_cuisine_and_city():
    agent = make_agent()
    response = agent.parse_and_execute("חפש איטלקי בתל אביב")
    assert "לה פיאצה" in response


def test_search_no_results():
    agent = make_agent()
    response = agent.parse_and_execute("חפש הודי")
    assert "לא נמצאו" in response


def test_implicit_search():
    agent = make_agent()
    response = agent.parse_and_execute("סושי בתל אביב")
    assert "סאקורה" in response


def test_search_stores_results():
    agent = make_agent()
    agent.parse_and_execute("חפש ישראלי")
    assert len(agent.last_search_results) == 2


def test_reservation_flow():
    agent = make_agent()
    # First search
    agent.parse_and_execute("חפש איטלקי בתל אביב")
    # Then reserve
    response = agent.parse_and_execute("הזמן 1 ל-15/03/2026 בשעה 20:00 ל-4 סועדים")
    assert response == "NEED_CUSTOMER_INFO"
    # Complete with customer info
    response = agent.complete_reservation("ישראל ישראלי", "050-1234567")
    assert "אושרה" in response
    assert "לה פיאצה" in response


def test_reservation_missing_date():
    agent = make_agent()
    agent.parse_and_execute("חפש איטלקי")
    response = agent.parse_and_execute("הזמן 1 בשעה 20:00 ל-4 סועדים")
    assert "תאריך" in response


def test_reservation_missing_time():
    agent = make_agent()
    agent.parse_and_execute("חפש איטלקי")
    response = agent.parse_and_execute("הזמן 1 ל-15/03/2026 ל-4 סועדים")
    assert "שעה" in response


def test_reservation_missing_party_size():
    agent = make_agent()
    agent.parse_and_execute("חפש איטלקי")
    response = agent.parse_and_execute("הזמן 1 ל-15/03/2026 בשעה 20:00")
    assert "סועדים" in response


def test_reservation_no_search_first():
    agent = make_agent()
    response = agent.parse_and_execute("הזמן 1 ל-15/03/2026 בשעה 20:00 ל-4 סועדים")
    assert "מסעדה מתוצאות" in response


def test_cancel_reservation():
    agent = make_agent()
    agent.parse_and_execute("חפש איטלקי בתל אביב")
    agent.parse_and_execute("הזמן 1 ל-15/03/2026 בשעה 20:00 ל-4 סועדים")
    result = agent.complete_reservation("ישראל ישראלי", "050-1234567")
    # Extract reservation ID
    import re
    match = re.search(r"מספר הזמנה: ([a-f0-9]{8})", result)
    assert match
    res_id = match.group(1)

    response = agent.parse_and_execute(f"בטל {res_id}")
    assert "בוטלה בהצלחה" in response


def test_cancel_invalid_id():
    agent = make_agent()
    response = agent.parse_and_execute("בטל xyz")
    assert "מספר הזמנה" in response


def test_my_reservations():
    agent = make_agent()
    agent.parse_and_execute("חפש איטלקי בתל אביב")
    agent.parse_and_execute("הזמן 1 ל-15/03/2026 בשעה 20:00 ל-4 סועדים")
    agent.complete_reservation("ישראל ישראלי", "050-1234567")

    response = agent.parse_and_execute("הזמנות שלי 050-1234567")
    assert "לה פיאצה" in response
    assert "15/03/2026" in response


def test_my_reservations_no_phone():
    agent = make_agent()
    response = agent.parse_and_execute("הזמנות שלי")
    assert "מספר טלפון" in response


def test_my_reservations_none_found():
    agent = make_agent()
    response = agent.parse_and_execute("הזמנות שלי 050-9999999")
    assert "לא נמצאו" in response


def test_unknown_command():
    agent = make_agent()
    response = agent.parse_and_execute("דבר חסר משמעות")
    assert "לא הבנתי" in response


def test_empty_input():
    agent = make_agent()
    response = agent.parse_and_execute("")
    assert "לא הבנתי" in response


def test_price_search():
    agent = make_agent()
    response = agent.parse_and_execute("חפש מסעדה יוקרתית")
    assert "סאקורה" in response or "ביסטרו פריז" in response
