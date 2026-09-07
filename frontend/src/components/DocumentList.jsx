import UploadButton from './UploadButton'

function statusLabel(doc) {
  if (doc.status === 'processing') return 'Processing…'
  if (doc.status === 'failed') return doc.error_message || 'Failed to process'
  return `${doc.num_pages} pages · ${doc.num_chunks} chunks`
}

export default function DocumentList({ documents, activeDocId, onSelect, onDelete, onUploaded }) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="brand">DocuChat</div>
        <div className="tagline">Chat with your PDF documents</div>
      </div>

      <UploadButton onUploaded={onUploaded} />

      <div className="doc-list">
        {documents.length === 0 && (
          <div className="doc-list-empty">
            No documents yet. Upload a PDF to start a conversation with it.
          </div>
        )}
        {documents.map((doc) => (
          <div
            key={doc.id}
            className={`doc-item ${doc.id === activeDocId ? 'active' : ''}`}
            onClick={() => onSelect(doc)}
          >
            <span className="doc-icon">📄</span>
            <div className="doc-meta">
              <div className="doc-name">{doc.filename}</div>
              <div className={`doc-sub status-${doc.status}`}>{statusLabel(doc)}</div>
            </div>
            <button
              className="doc-delete"
              title="Delete document"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(doc.id)
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
