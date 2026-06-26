# התקנה והרצה ב-Termux

המדריך מיועד להרצה על Android דרך Termux.

## התקנת חבילות מערכת

```sh
pkg update
pkg install -y python clang libxml2 libxslt
```

החבילות `libxml2` ו־`libxslt` נדרשות עבור `lxml`.

## התקנת הפרויקט

```sh
cd /data/data/com.termux/files/home
cd pais/chance-fastapi
chmod +x scripts/install.sh scripts/run.sh run.sh
./scripts/install.sh
```

## הרצה חוזרת אחרי התקנה

```sh
cd /data/data/com.termux/files/home/pais/chance-fastapi
./run.sh
```

## גישה מהטלפון

```text
http://127.0.0.1:8000/latest
```

אם רוצים לגשת ממכשיר אחר באותה רשת, בדקו את כתובת ה־IP של הטלפון:

```sh
ip addr
```

ואז פתחו:

```text
http://PHONE_IP:8000/latest
```

## תקלות נפוצות ב-Termux

### `No module named pytest`

התלויות לא הותקנו בסביבה הפעילה:

```sh
. .venv/bin/activate
pip install -r requirements.txt
```

### שגיאה בבניית `lxml`

ודאו שחבילות המערכת מותקנות:

```sh
pkg install -y clang libxml2 libxslt
pip install -r requirements.txt
```

### פורט תפוס

```sh
PORT=8010 ./run.sh
```

### בדיקת fetch ידנית

```sh
curl -X POST http://127.0.0.1:8000/refresh
curl http://127.0.0.1:8000/latest
```
