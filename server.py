import os
import json
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

# --- Menu Data ---

MENU = [
    {"id": 1, "name": "מרגריטה", "description": "רוטב עגבניות, מוצרלה, בזיליקום טרי", "price": 49, "image": "🍕"},
    {"id": 2, "name": "פפרוני", "description": "רוטב עגבניות, מוצרלה, פפרוני מתובל", "price": 55, "image": "🍕"},
    {"id": 3, "name": "ארבע גבינות", "description": "מוצרלה, גאודה, פרמזן, גורגונזולה", "price": 59, "image": "🧀"},
    {"id": 4, "name": "ירקות הגינה", "description": "פלפלים, זיתים, פטריות, בצל, עגבניות", "price": 52, "image": "🥬"},
    {"id": 5, "name": "טונה", "description": "רוטב עגבניות, מוצרלה, טונה, בצל סגול", "price": 55, "image": "🐟"},
    {"id": 6, "name": "בולונז", "description": "רוטב בולונז עשיר, מוצרלה, בזיליקום", "price": 58, "image": "🍖"},
    {"id": 7, "name": "משפחתית מיקס", "description": "חצי-חצי לבחירתכם, גודל XL", "price": 79, "image": "🍕"},
    {"id": 8, "name": "מתוקה", "description": "נוטלה, בננה, אגוזים, אבקת סוכר", "price": 45, "image": "🍫"},
]

TOPPINGS = [
    {"id": 1, "name": "מוצרלה נוספת", "price": 5},
    {"id": 2, "name": "זיתים", "price": 4},
    {"id": 3, "name": "פטריות", "price": 4},
    {"id": 4, "name": "בצל", "price": 3},
    {"id": 5, "name": "פלפל חריף", "price": 3},
    {"id": 6, "name": "תירס", "price": 4},
]

# --- In-memory orders store ---

orders: list[dict] = []


# --- Models ---

class OrderItem(BaseModel):
    pizza_id: int
    quantity: int
    toppings: list[int] = []


class Order(BaseModel):
    name: str
    phone: str
    address: str
    items: list[OrderItem]
    notes: str = ""


# --- API Routes ---

@app.get("/api/menu")
async def get_menu():
    return {"pizzas": MENU, "toppings": TOPPINGS}


@app.post("/api/order")
async def place_order(order: Order):
    # Calculate total
    total = 0
    order_details = []
    for item in order.items:
        pizza = next((p for p in MENU if p["id"] == item.pizza_id), None)
        if not pizza:
            return {"success": False, "error": f"פיצה לא נמצאה: {item.pizza_id}"}
        item_price = pizza["price"] * item.quantity
        for tid in item.toppings:
            topping = next((t for t in TOPPINGS if t["id"] == tid), None)
            if topping:
                item_price += topping["price"] * item.quantity
        total += item_price
        order_details.append({
            "pizza": pizza["name"],
            "quantity": item.quantity,
            "toppings": [t["name"] for t in TOPPINGS if t["id"] in item.toppings],
            "price": item_price,
        })

    order_record = {
        "id": len(orders) + 1,
        "name": order.name,
        "phone": order.phone,
        "address": order.address,
        "items": order_details,
        "notes": order.notes,
        "total": total,
        "time": datetime.now().isoformat(),
    }
    orders.append(order_record)

    return {
        "success": True,
        "order_id": order_record["id"],
        "total": total,
        "message": f"ההזמנה התקבלה! מספר הזמנה: {order_record['id']}. סה\"כ: ₪{total}",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
