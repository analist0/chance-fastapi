# chance-fastapi

שירות FastAPI לאיסוף רציף של תוצאות הגרלת צ'אנס מאתר מפעל הפיס הרשמי.

המערכת מושכת נתונים מהמקור הרשמי, שומרת אותם ב־SQLite, מונעת כפילויות, ומספקת API פשוט לקבלת התוצאה האחרונה, היסטוריה, רענון ידני וסטטיסטיקות.

> הערה משפטית: התוצאות באתר מפעל הפיס הן המקור הרשמי. השירות הזה נועד לאיסוף, ניטור ותצוגה טכנית בלבד.

## מה המערכת עושה

- מושכת תוצאות צ'אנס באופן אוטומטי כל 30 שניות.
- משתמשת קודם במקור structured רשמי: קובץ CSV מאתר מפעל הפיס.
- מעשירה את התוצאה האחרונה דרך AJAX HTML רשמי כדי לקבל גם שעת הגרלה.
- שומרת נתונים ב־SQLite.
- מונעת כפילויות לפי `draw_id`.
- חושפת REST API דרך FastAPI.
- כוללת לוגים מסתובבים, בדיקות, Docker, Docker Compose ותמיכה ב־Termux.

## ניתוח מקור הנתונים

לפני כתיבת הקוד נבדקו עמודי צ'אנס הרשמיים:

- עמוד ראשי: `https://www.pais.co.il/chance/`
- ארכיון: `https://www.pais.co.il/chance/archive.aspx`
- JavaScript כללי: `/include/script.js?v=02`
- JavaScript סטטיסטיקות: `/Statistics/Statistics.js`

ממצאים:

- האתר בנוי כ־ASP.NET WebForms וכולל `__VIEWSTATE`.
- ארכיון התוצאות נטען דרך AJAX:
  `https://www.pais.co.il/chance/showMoreResults.aspx?fromIndex=0&amount=12`
- קיים מקור CSV רשמי:
  `https://www.pais.co.il/chance/chance_resultsDownload.aspx`
- קיים endpoint סטטיסטיקות `/statistics/Statistics.ashx`, אך הוא מיועד לחישובים סטטיסטיים ולא להזנת תוצאה אחרונה.

לכן המימוש משתמש ב־CSV הרשמי כמקור ראשי, וב־AJAX HTML הרשמי כמקור העשרה וגיבוי.

## מבנה הריפו

```text
chance-fastapi/
  app/
    main.py          # יצירת FastAPI וחיבור lifecycle
    api.py           # כל נתיבי ה-REST
    scraper.py       # משיכת נתונים אסינכרונית
    parser.py        # פענוח CSV / JSON / HTML / AJAX
    database.py      # SQLAlchemy + SQLite
    models.py        # מודלי Pydantic ו-SQLAlchemy
    scheduler.py     # APScheduler כל 30 שניות
    config.py        # הגדרות דרך env
    logger.py        # loguru + rotation
    utils.py         # פונקציות עזר
  tests/
  scripts/
  docs/
  Dockerfile
  docker-compose.yml
  requirements.txt
```

## התקנה מהירה

```sh
cd chance-fastapi
chmod +x scripts/install.sh scripts/run.sh run.sh
./scripts/install.sh
```

הסקריפט:

1. יוצר virtualenv.
2. מתקין תלויות.
3. מריץ בדיקות.
4. יוצר DB.
5. מבצע fetch ראשון מהאתר הרשמי.
6. מדפיס `SUCCESS` או `FAILURE`.
7. מפעיל את FastAPI.

## הרצה רגילה

```sh
cd chance-fastapi
./run.sh
```

ברירת מחדל:

```text
http://localhost:8000
```

## שימוש ב־API

```sh
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/latest
curl 'http://localhost:8000/history?limit=20'
curl -X POST http://localhost:8000/refresh
curl http://localhost:8000/stats
```

דוגמת תשובה מ־`GET /latest`:

```json
{
  "draw_id": 53125,
  "date": "2026-06-25",
  "time": "21:00",
  "cards": [
    {"suit": "clubs", "suit_he": "תלתן", "rank": "A"},
    {"suit": "diamonds", "suit_he": "יהלום", "rank": "J"},
    {"suit": "hearts", "suit_he": "לב", "rank": "K"},
    {"suit": "spades", "suit_he": "עלה", "rank": "A"}
  ],
  "game_type": "Chance",
  "source": "official_csv+official_ajax_html",
  "fetched_at": "2026-06-26T05:15:14.831635"
}
```

## Docker

```sh
docker compose up --build
```

לאחר העלייה:

```sh
curl http://localhost:8000/latest
```

## Termux

```sh
pkg update
pkg install -y python clang libxml2 libxslt
cd chance-fastapi
chmod +x scripts/install.sh
./scripts/install.sh
```

פירוט מלא נמצא ב־[docs/TERMUX.md](docs/TERMUX.md).

## התקנה לפי מערכת הפעלה

מדריך מלא נמצא ב־[docs/INSTALL.md](docs/INSTALL.md), כולל:

- Linux
- macOS
- Windows
- Docker
- Docker Compose
- Termux באנדרואיד

## מסמכים נוספים

- [ארכיטקטורה](docs/ARCHITECTURE.md)
- [מדריך API](docs/API.md)
- [Docker ו-Compose](docs/DOCKER.md)
- [Termux](docs/TERMUX.md)
- [תפעול, לוגים ופתרון תקלות](docs/OPERATIONS.md)
- [תרומה לפרויקט](CONTRIBUTING.md)

## בדיקות

```sh
pytest -q
```

## משתני סביבה

ראו [.env.example](.env.example).

משתנים חשובים:

- `FETCH_INTERVAL_SECONDS` - ברירת מחדל `30`.
- `DATABASE_URL` - ברירת מחדל `sqlite:///chance.db`.
- `LOG_DIR` - ברירת מחדל `logs`.
- `REQUEST_TIMEOUT_SECONDS` - timeout לכל בקשת HTTP.
- `REQUEST_RETRIES` - מספר ניסיונות חוזרים.

## רישיון

MIT. ראו [LICENSE](LICENSE).
