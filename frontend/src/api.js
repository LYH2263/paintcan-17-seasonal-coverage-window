export async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
async function sendJSON(path, body, method) {
  const r = await fetch(path, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
export const postJSON = (path, body) => sendJSON(path, body, 'POST')
export const putJSON = (path, body) => sendJSON(path, body, 'PUT')
