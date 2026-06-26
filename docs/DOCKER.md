# Docker

## בנייה והרצה ידנית

```sh
cd chance-fastapi
docker build -t chance-fastapi .
docker run --rm -p 8000:8000 chance-fastapi
```

בדיקה:

```sh
curl http://localhost:8000/latest
```

## Docker Compose

```sh
docker compose up --build
```

ה־Compose מגדיר:

- port `8000`.
- volume ל־SQLite תחת `./data`.
- volume ללוגים תחת `./logs`.
- restart policy: `unless-stopped`.

## משתני סביבה ב־Compose

```yaml
environment:
  FETCH_INTERVAL_SECONDS: "30"
  DATABASE_URL: "sqlite:////app/data/chance.db"
  LOG_DIR: "/app/logs"
```

## עצירת השירות

```sh
docker compose down
```

מחיקת נתונים מקומיים:

```sh
docker compose down
rm -rf data logs
```

## בדיקת לוגים

```sh
docker compose logs -f
```
