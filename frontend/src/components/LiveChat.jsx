import { useCallback, useEffect, useRef, useState } from 'react'
import {
  formatTime,
  getSessionId,
  getVisitorName,
  sendMessageRest,
  setVisitorName,
  wsChatUrl,
} from '../api/chat'

export default function LiveChat() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [name, setName] = useState(getVisitorName())
  const [nameDraft, setNameDraft] = useState(getVisitorName())
  const [connected, setConnected] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  const sessionId = useRef(getSessionId())
  const wsRef = useRef(null)
  const listRef = useRef(null)

  const scrollDown = useCallback(() => {
    requestAnimationFrame(() => {
      if (listRef.current) {
        listRef.current.scrollTop = listRef.current.scrollHeight
      }
    })
  }, [])

  const appendMessage = useCallback((msg) => {
    setMessages((prev) => {
      if (prev.some((m) => m.id === msg.id)) return prev
      return [...prev, msg]
    })
    scrollDown()
  }, [scrollDown])

  const connectWs = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(wsChatUrl(sessionId.current))
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => {
      setConnected(false)
      wsRef.current = null
    }
    ws.onerror = () => setError('Нет связи с сервером чата')
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'history') {
          setMessages(data.messages || [])
          scrollDown()
        } else if (data.type === 'message' && data.message) {
          appendMessage(data.message)
        }
      } catch {
        /* ignore */
      }
    }
  }, [appendMessage, scrollDown])

  useEffect(() => {
    if (!open) return

    setError('')
    connectWs()

    return () => {
      wsRef.current?.close()
      wsRef.current = null
    }
  }, [open, connectWs])

  const saveName = () => {
    const trimmed = nameDraft.trim()
    if (trimmed) {
      setVisitorName(trimmed)
      setName(trimmed)
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    setSending(true)
    setError('')
    setInput('')

    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ text, visitor_name: name || null }))
      } else {
        const msg = await sendMessageRest(sessionId.current, text, name)
        appendMessage(msg)
      }
    } catch {
      setError('Не удалось отправить. Проверьте, что API запущен.')
      setInput(text)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="live-chat">
      {open && (
        <div className="live-chat-panel" role="dialog" aria-label="Онлайн-чат поддержки">
          <div className="live-chat-header">
            <div>
              <strong>Поддержка</strong>
              <span className={`live-chat-status ${connected ? 'online' : 'offline'}`}>
                {connected ? 'онлайн' : 'подключение…'}
              </span>
            </div>
            <button type="button" className="live-chat-close" onClick={() => setOpen(false)} aria-label="Закрыть">
              ×
            </button>
          </div>

          {!name && (
            <div className="live-chat-name">
              <input
                type="text"
                placeholder="Ваше имя (необязательно)"
                value={nameDraft}
                onChange={(e) => setNameDraft(e.target.value)}
                maxLength={128}
              />
              <button type="button" onClick={saveName}>OK</button>
            </div>
          )}

          <div className="live-chat-messages" ref={listRef}>
            {messages.length === 0 && !error && (
              <p className="live-chat-empty">Загрузка сообщений…</p>
            )}
            {messages.map((msg) => (
              <div key={msg.id} className={`live-chat-bubble ${msg.role}`}>
                <p>{msg.text}</p>
                <time>{formatTime(msg.created_at)}</time>
              </div>
            ))}
          </div>

          {error && <p className="live-chat-error">{error}</p>}

          <form className="live-chat-form" onSubmit={handleSend}>
            <input
              type="text"
              placeholder="Напишите сообщение…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              maxLength={2000}
              disabled={sending}
            />
            <button type="submit" disabled={sending || !input.trim()}>
              ➤
            </button>
          </form>
        </div>
      )}

      <button
        type="button"
        className="live-chat-toggle"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        {open ? '✕' : '💬'}
        {!open && <span className="live-chat-toggle-label">Чат</span>}
      </button>
    </div>
  )
}
