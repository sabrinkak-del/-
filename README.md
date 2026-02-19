# פיצה נאפולי 🍕

אתר פיצרייה עם דף תדמית ומערכת הזמנות אונליין. בנוי עם Python + FastAPI ופרונט וניל HTML/CSS/JS בעברית (RTL).

## תכונות

- דף נחיתה עם מידע על הפיצרייה
- תפריט פיצות דינמי עם תוספות
- עגלת קניות עם סיכום הזמנה
- טופס הזמנה עם שם, טלפון, כתובת והערות
- עיצוב רספונסיבי (מובייל + דסקטופ)
- הכל בעברית עם תמיכה מלאה ב-RTL

## דרישות

- Python 3.11+

## התקנה והרצה

```bash
python -m venv venv
source venv/bin/activate  # ב-Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

פתחו http://localhost:8000 בדפדפן.

## מבנה הפרויקט

```
├── server.py          # שרת FastAPI + API הזמנות + תפריט
├── static/
│   ├── index.html     # דף הבית + תפריט + הזמנה + צור קשר
│   ├── style.css      # עיצוב RTL
│   └── app.js         # לוגיקת עגלה והזמנות
├── requirements.txt   # דרישות Python
└── .env.example       # משתני סביבה
```

## API

| מתודה | נתיב | תיאור |
|-------|------|-------|
| `GET` | `/api/menu` | מחזיר תפריט פיצות ותוספות |
| `POST` | `/api/order` | שולח הזמנה חדשה |
| `GET` | `/api/health` | בדיקת תקינות |
