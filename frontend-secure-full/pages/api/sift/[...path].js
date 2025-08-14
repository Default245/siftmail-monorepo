
export default async function handler(req, res) {
  const { path = [] } = req.query;
  const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
  const API_KEY = process.env.SIFT_API_KEY;
  const url = `${BACKEND_URL}/${path.join('/')}${req.url.includes('?') ? '?' + req.url.split('?')[1] : ''}`;

  const headers = { ...req.headers, 'x-api-key': API_KEY, 'content-type': req.headers['content-type'] || 'application/json' };
  delete headers.host;

  const init = {
    method: req.method,
    headers,
    body: ['GET','HEAD'].includes(req.method) ? undefined : (typeof req.body === 'string' ? req.body : JSON.stringify(req.body || {})),
  };

  try{
    const r = await fetch(url, init);
    const text = await r.text();
    res.status(r.status).send(text);
  }catch(e){
    res.status(500).json({ error: 'proxy_error', detail: String(e) });
  }
}
