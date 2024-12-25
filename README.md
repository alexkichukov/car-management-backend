# Car Management Backend

## Setup

### Create a virtual environment:

```bash
python -m venv .venv
```

### Activate the virtual environment:

on Windows:
```bash
.venv\Scripts\Activate.ps1
```
on Linux or macOS:
```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Run development server

```bash
fastapi dev main.py --port 8088
```