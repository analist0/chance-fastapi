# ארכיטקטורה

## זרימת מידע

```text
מפעל הפיס
  |
  |-- CSV רשמי: /chance/chance_resultsDownload.aspx
  |-- AJAX HTML: /chance/showMoreResults.aspx
  |
scraper.py
  |
parser.py
  |
database.py -> SQLite
  |
api.py -> FastAPI REST API
```

## שכבות המערכת

### `scraper.py`

אחראי למשיכת הנתונים מהרשת.

מאפיינים:

- `httpx.AsyncClient`
- headers דמויי דפדפן
- `gzip`, redirects ו־timeout
- retries עם backoff
- זיהוי חסימות בסיסי לפי status code ותוכן
- לוג לכל בקשה

### `parser.py`

אחראי לפענוח התגובה.

הסדר:

1. CSV רשמי.
2. JSON אם מתקבלת תגובת JSON.
3. AJAX HTML של ארכיון.
4. HTML כללי של עמוד צ'אנס.
5. script tags עם JSON מוטמע, אם קיימים.

הפענוח אינו תלוי ב־selector יחיד. הוא מחפש:

- שורות CSV.
- פריטי ארכיון.
- טבלאות.
- divים.
- תגיות script.
- טקסטים עם מספר הגרלה, תאריך, שעה וקלפים.

### `database.py`

שכבת persistence עם SQLAlchemy.

טבלת `chance_draws` שומרת:

- `draw_id`
- `draw_date`
- `draw_time`
- `cards_json`
- `raw_response`
- `source`
- `fetched_at`
- `created_at`
- `updated_at`

מניעת כפילות מתבצעת עם unique constraint על `draw_id`.

### `scheduler.py`

מריץ refresh אוטומטי כל `FETCH_INTERVAL_SECONDS`.

ברירת מחדל:

```text
30 seconds
```

ה־scheduler מוגדר ל־UTC כדי לא להיות תלוי ב־timezone database מקומי.

### `api.py`

נתיבי REST:

- `GET /`
- `GET /health`
- `GET /latest`
- `GET /history`
- `POST /refresh`
- `GET /stats`

### `logger.py`

משתמש ב־loguru:

- stderr בזמן פיתוח.
- קובץ `logs/chance-fastapi.log`.
- rotation בגודל `10 MB`.
- retention של `14 days`.

## למה CSV קודם

בבדיקה התברר שהאתר הרשמי מספק CSV מלא דרך:

```text
/chance/chance_resultsDownload.aspx
```

זה מקור structured, יציב יותר מ־HTML, ולכן הוא המקור הראשי.

ה־CSV לא כולל שעה לכל הגרלה. לכן המערכת מושכת גם את AJAX archive fragment כדי להעשיר את התוצאות האחרונות בשעה הרשמית.

## אימות אחרי fetch

אחרי כל fetch המערכת בודקת:

- נמצאו תוצאות.
- לכל הגרלה יש 4 קלפים.
- אין כפילות `draw_id` באותו fetch.
- האם מספר ההגרלה האחרון השתנה.

## עקרונות תכנון

- שמירה על קוד אסינכרוני בשכבת הרשת.
- הפרדה בין scraping, parsing, database ו־API.
- העדפת מקור structured רשמי על פני scraping.
- fallback ל־HTML רק כשצריך.
- שמירת raw response כדי לאפשר debugging.
