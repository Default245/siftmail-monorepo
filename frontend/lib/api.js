const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function handleResponse(response) {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Request failed');
  }
  return response.json();
}

export async function classifyMessage(payload) {
  const response = await fetch(`${apiBase}/api/sift/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function classifyBatch(payload) {
  const response = await fetch(`${apiBase}/api/sift/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function fetchHealth() {
  const response = await fetch(`${apiBase}/health`);
  return handleResponse(response);
}
