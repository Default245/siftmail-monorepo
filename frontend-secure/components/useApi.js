
export async function apiGet(path){
  const r = await fetch(`/api/sift/${path}`, { method: 'GET' });
  if(!r.ok) throw new Error(await r.text());
  const ct = r.headers.get('content-type') || '';
  return ct.includes('application/json') ? r.json() : r.text();
}
export async function apiPost(path, body){
  const r = await fetch(`/api/sift/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  });
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}
