export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div>
        <div className="message-bubble">{message.content}</div>
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="sources">
            {message.sources.map((s, i) => (
              <span className="source-pill" key={i}>
                📄 {s.document ? `${s.document} — ` : ''}Page {s.page}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
