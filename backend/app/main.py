from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'SiftMail backend running'}

@app.post('/api/sift/classify')
def classify():
    return {'result': 'classified'}

@app.post('/api/sift/batch')
def batch():
    return {'results': []}