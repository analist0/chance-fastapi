# מדריך API

ברירת מחדל:

```text
http://localhost:8000
```

## `GET /`

מידע בסיסי על השירות.

```sh
curl http://localhost:8000/
```

## `GET /health`

בדיקת בריאות.

```sh
curl http://localhost:8000/health
```

דוגמה:

```json
{
  "status": "ok",
  "has_latest": true
}
```

## `GET /latest`

מחזיר את הגרלת צ'אנס האחרונה שנשמרה.

```sh
curl http://localhost:8000/latest
```

דוגמה:

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

## `GET /history`

מחזיר היסטוריה לפי סדר יורד של מספר הגרלה.

פרמטרים:

- `limit` - בין 1 ל־500, ברירת מחדל 50.
- `offset` - ברירת מחדל 0.

```sh
curl 'http://localhost:8000/history?limit=20&offset=0'
```

## `POST /refresh`

מריץ fetch ידני עכשיו.

```sh
curl -X POST http://localhost:8000/refresh
```

דוגמה:

```json
{
  "success": true,
  "inserted": 0,
  "updated": 0,
  "duplicate_count": 48795,
  "latest": {
    "draw_id": 53125,
    "date": "2026-06-25",
    "time": "21:00",
    "cards": [
      {"suit": "clubs", "suit_he": "תלתן", "rank": "A"},
      {"suit": "diamonds", "suit_he": "יהלום", "rank": "J"},
      {"suit": "hearts", "suit_he": "לב", "rank": "K"},
      {"suit": "spades", "suit_he": "עלה", "rank": "A"}
    ]
  },
  "validation": {
    "cards_count_valid": true,
    "no_duplicate_draw_ids_in_fetch": true,
    "draw_changed": false,
    "parsed_count": 48795
  }
}
```

## `GET /stats`

מחזיר סטטיסטיקת אחסון בסיסית.

```sh
curl http://localhost:8000/stats
```

דוגמה:

```json
{
  "total_draws": 48795,
  "latest_draw_id": 53125,
  "oldest_draw_id": 1,
  "last_fetch_at": "2026-06-26T05:15:14.831635",
  "draw_changed": false
}
```

## קודי שגיאה נפוצים

- `404` ב־`/latest`: עדיין אין נתונים. הריצו `POST /refresh`.
- `502` ב־`/refresh`: בעיית fetch או parsing מול האתר הרשמי.
