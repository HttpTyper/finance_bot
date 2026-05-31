const SESSION_KEY = 'fs_chat_session_id'
const NAME_KEY = 'fs_chat_visitor_name'

export function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(SESSION_KEY, id)
  }
  return id
}

export function getVisitorName() {
  return localStorage.getItem(NAME_KEY) || ''
}

export function setVisitorName(name) {
  localStorage.setItem(NAME_KEY, name.trim())
}

function apiBase() {
  return (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '')
}

export function wsChatUrl(sessionId) {
  const base = apiBase()
  if (base) {
    const wsBase = base.replace(/^http/i, 'ws')
    return `${wsBase}/api/chat/ws/${sessionId}`
  }
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}/api/chat/ws/${sessionId}`
}

export function httpChatUrl(path) {
  const base = apiBase()
  return base ? `${base}${path}` : path
}

export async function fetchHistory(sessionId) {
  const res = await fetch(httpChatUrl(`/api/chat/sessions/${sessionId}/messages`))
  if (!res.ok) throw new Error('Не удалось загрузить чат')
  return res.json()
}

export async function sendMessageRest(sessionId, text, visitorName) {
  const res = await fetch(httpChatUrl(`/api/chat/sessions/${sessionId}/messages`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, visitor_name: visitorName || null }),
  })
  if (!res.ok) throw new Error('Не удалось отправить сообщение')
  return res.json()
}

export function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}
