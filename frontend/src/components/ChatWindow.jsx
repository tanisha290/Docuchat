import { useEffect, useRef, useState } from 'react'
import MessageBubble from './MessageBubble'
import { createConversation, sendMessage } from '../api/client'

export default function ChatWindow({ document }) {
  const [conversation, setConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const scrollRef = useRef(null)

  // Start a fresh conversation whenever the selected document changes.
  useEffect(() => {
    let cancelled = false
    setMessages([])
    setConversation(null)
    setError(null)

    if (!document || document.status !== 'ready') return

    createConversation(document.id)
      .then(({ conversation }) => {
        if (!cancelled) setConversation(conversation)
      })
      .catch((err) => !cancelled && setError(err.message))

    return () => {
      cancelled = true
    }
  }, [document])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  async function handleSend() {
    const content = input.trim()
    if (!content || !conversation || sending) return

    setError(null)
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content, sources: [] }])
    setSending(true)

    try {
      const result = await sendMessage(conversation.id, content)
      setMessages((prev) => [...prev, { role: 'assistant', content: result.answer, sources: result.sources }])
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!document) {
    return (
      <div className="chat-panel">
        <div className="chat-empty-state">
          <div className="brand">DocuChat</div>
          <p>Upload a PDF on the left, then select it here to start asking questions about it.</p>
        </div>
      </div>
    )
  }

  if (document.status === 'processing') {
    return (
      <div className="chat-panel">
        <div className="chat-empty-state">
          <p>Still processing “{document.filename}”… this can take a moment for larger files.</p>
        </div>
      </div>
    )
  }

  if (document.status === 'failed') {
    return (
      <div className="chat-panel">
        <div className="chat-empty-state">
          <p>“{document.filename}” couldn't be processed: {document.error_message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span className="doc-name">{document.filename}</span>
        <span className="doc-pages">{document.num_pages} pages</span>
      </div>

      <div className="messages" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="messages-empty">Ask anything about this document to get started.</div>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {sending && <div className="thinking">DocuChat is thinking…</div>}
      </div>

      {error && <div className="chat-error">{error}</div>}

      <div className="chat-input-area">
        <textarea
          rows={1}
          placeholder="Ask a question about this document…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={!conversation || sending}
        />
        <button className="send-btn" onClick={handleSend} disabled={!conversation || sending || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  )
}
