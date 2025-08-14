
# Sift Mail — Backend (Advanced)

OAuth + Gmail APIs + batch classification + quarantine.

## Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
mkdir -p tokens

## Run
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
