# CLAUDE.md

## Project Overview

פיצה נאפולי — אתר פיצרייה בעברית עם דף תדמית ומערכת הזמנות אונליין. Python + FastAPI backend, vanilla HTML/CSS/JS frontend, RTL layout.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Frontend:** Vanilla HTML/CSS/JavaScript (no framework, no build step)
- **Language:** Hebrew (RTL), all UI text is in Hebrew
- **Static serving:** FastAPI `StaticFiles` mount

## Project Structure

```
├── server.py          # Backend: FastAPI app, menu API, order API
├── static/
│   ├── index.html     # Full page: hero, about, menu, order form, contact, footer
│   ├── style.css      # RTL styles, responsive, red/white color scheme
│   └── app.js         # Menu loading, cart state, toppings modal, order submission
├── requirements.txt   # fastapi, uvicorn, python-dotenv
├── .env.example       # PORT config
└── .gitignore         # Python + .env exclusions
```

## Key Architecture

- **Single `server.py`** — menu data is hardcoded in `MENU` and `TOPPINGS` lists. Orders stored in-memory (`orders` list). No database.
- **Two API endpoints:** `GET /api/menu` returns pizza + topping data, `POST /api/order` accepts an order and calculates total.
- **Frontend loads menu via `/api/menu`** on page load, renders cards dynamically.
- **Cart lives in JS memory** — `cart` array of `{pizza_id, quantity, toppings}`. Full cart sent with order request.
- **Static mount** at `/` serves `static/` directory. Must come after API route definitions.
- **RTL:** Set via `<html dir="rtl">` and `direction: rtl` in CSS. Cart sidebar slides from left.

## Development

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
python server.py
```
Server at http://localhost:8000 with auto-reload.

### Test API
```bash
# Get menu
curl http://localhost:8000/api/menu

# Place order
curl -X POST http://localhost:8000/api/order \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","phone":"050-1234567","address":"Test St 1","items":[{"pizza_id":1,"quantity":2,"toppings":[1]}]}'
```

## Conventions

- **All UI text in Hebrew** — keep RTL layout consistent
- **Prices in ₪ (NIS)**
- **Color scheme:** Red (#dc2626) primary, white background, dark navbar
- **No external dependencies on frontend** — no CDN, no npm, no build
- **Menu data in `server.py`** — edit `MENU` and `TOPPINGS` lists to change offerings
- **Pydantic models** for request validation: `OrderItem`, `Order`
