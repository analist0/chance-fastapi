# תפעול ופתרון תקלות

## קבצים חשובים

- DB מקומי: `chance.db`
- לוגים: `logs/chance-fastapi.log`
- הגדרות לדוגמה: `.env.example`

## לוגים

המערכת כותבת לוגים ל־stderr ולקובץ:

```text
logs/chance-fastapi.log
```

צפייה בזמן אמת:

```sh
tail -f logs/chance-fastapi.log
```

הלוגים עוברים rotation בגודל 10MB ונשמרים 14 ימים.

## שינוי תדירות משיכה

ברירת מחדל היא 30 שניות.

```sh
FETCH_INTERVAL_SECONDS=60 ./run.sh
```

או ב־Docker Compose:

```yaml
environment:
  FETCH_INTERVAL_SECONDS: "60"
```

## רענון ידני

```sh
curl -X POST http://localhost:8000/refresh
```

## בדיקת מצב

```sh
curl http://localhost:8000/health
curl http://localhost:8000/stats
```

## גיבוי SQLite

```sh
sqlite3 chance.db ".backup chance.backup.db"
```

אם אין `sqlite3`, אפשר לעצור את השירות ולהעתיק את הקובץ:

```sh
cp chance.db chance.backup.db
```

## איפוס נתונים

עצרו את השירות ואז:

```sh
rm -f chance.db chance.db-*
```

בהפעלה הבאה הטבלאות ייווצרו מחדש.

## תקלות נפוצות

### `POST /refresh` מחזיר 502

סיבות אפשריות:

- האתר הרשמי לא זמין זמנית.
- חסימת רשת.
- שינוי מבנה באתר מפעל הפיס.
- timeout נמוך מדי.

פעולות:

```sh
curl -I https://www.pais.co.il/chance/chance_resultsDownload.aspx
curl -X POST http://localhost:8000/refresh
tail -n 100 logs/chance-fastapi.log
```

### אין נתונים ב־`/latest`

הריצו:

```sh
curl -X POST http://localhost:8000/refresh
```

אם עדיין אין נתונים, בדקו לוגים.

### השרת לא עולה

בדקו שהפורט פנוי:

```sh
PORT=8010 ./run.sh
```

### בדיקות נכשלות בגלל תלויות

התקינו מחדש:

```sh
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest -q
```
