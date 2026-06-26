# תרומה לפרויקט

תודה על הרצון לתרום ל־`chance-fastapi`.

## סביבת פיתוח

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## כללי קוד

- שמרו על טיפוסים ברורים.
- אל תוסיפו scraping לפי selector יחיד בלי fallback.
- העדיפו מקור structured רשמי אם קיים.
- כל שינוי ב־parser צריך לכלול בדיקה.
- אין לשמור secrets בריפו.

## לפני Pull Request

```sh
pytest -q
curl -X POST http://localhost:8000/refresh
curl http://localhost:8000/latest
```

## שינויי תיעוד

התיעוד המרכזי בעברית נמצא ב:

- `README.md`
- `docs/`

עדכנו אותם כשמשנים התנהגות, משתני סביבה או תהליך התקנה.
