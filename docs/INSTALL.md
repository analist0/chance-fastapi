# מדריך התקנה

מסמך זה מפרט התקנה והרצה של `chance-fastapi` במערכות הפעלה נפוצות.

## דרישות כלליות

- Python 3.11 ומעלה.
- גישה לאינטרנט אל `https://www.pais.co.il`.
- `pip`.
- מומלץ: `git`.

## Linux

### Debian / Ubuntu

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential libxml2-dev libxslt1-dev
cd chance-fastapi
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest -q
./run.sh
```

### Fedora

```sh
sudo dnf install -y python3 python3-pip gcc libxml2-devel libxslt-devel
cd chance-fastapi
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest -q
./run.sh
```

### Arch Linux

```sh
sudo pacman -Syu --needed python python-pip base-devel libxml2 libxslt
cd chance-fastapi
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest -q
./run.sh
```

## macOS

עם Homebrew:

```sh
brew install python libxml2 libxslt
cd chance-fastapi
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest -q
./run.sh
```

אם `lxml` נכשל בהתקנה, ודאו ש־Homebrew מותקן ומעודכן:

```sh
brew update
brew upgrade
```

## Windows

### PowerShell

התקינו Python 3.11+ מאתר Python הרשמי או דרך winget:

```powershell
winget install Python.Python.3.13
```

לאחר מכן:

```powershell
cd chance-fastapi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

אם PowerShell חוסם הפעלת virtualenv:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows עם WSL

מומלץ להשתמש ב־Ubuntu תחת WSL:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential libxml2-dev libxslt1-dev
cd chance-fastapi
./scripts/install.sh
```

## Docker

```sh
cd chance-fastapi
docker build -t chance-fastapi .
docker run --rm -p 8000:8000 chance-fastapi
```

או עם Compose:

```sh
docker compose up --build
```

## Termux

```sh
pkg update
pkg install -y python clang libxml2 libxslt
cd chance-fastapi
./scripts/install.sh
```

פירוט נוסף: [TERMUX.md](TERMUX.md).

## בדיקת התקנה

אחרי שהשרת עולה:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/latest
```

תשובת `health` תקינה:

```json
{"status":"ok","has_latest":true}
```
