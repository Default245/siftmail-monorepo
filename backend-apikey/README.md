
# SiftMail Backend (API Key protected)

All endpoints require the header: `X-API-Key: <your key>`.

## Run
```bash
pip install -r requirements.txt
# set your API key
cp .env.example .env && nano .env
uvicorn main:app --reload --port 8080
```

## Example
```bash
curl -H "X-API-Key: YOUR_KEY" http://localhost:8080/health
```

### Batch classify
```bash
curl -X POST http://localhost:8080/classify_batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '[{"id":"1","subject":"Win a FREE prize","sender":"promo@x.com","body":"Buy now"}, {"id":"2","subject":"Team update","sender":"ceo@acme.com","body":"Weekly notes"}]'
```
