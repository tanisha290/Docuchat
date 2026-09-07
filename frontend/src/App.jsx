import { useEffect, useState, useCallback } from 'react'
import DocumentList from './components/DocumentList'
import ChatWindow from './components/ChatWindow'
import { listDocuments, deleteDocument } from './api/client'

const POLL_INTERVAL_MS = 3000

export default function App() {
  const [documents, setDocuments] = useState([])
  const [activeDoc, setActiveDoc] = useState(null)

  const refresh = useCallback(async () => {
    try {
      const { documents } = await listDocuments()
      setDocuments(documents)
      // Keep the active doc's status in sync (e.g. processing -> ready).
      setActiveDoc((prev) => {
        if (!prev) return prev
        return documents.find((d) => d.id === prev.id) || prev
      })
    } catch {
      // Silently ignore — the UI will just retry on the next poll.
    }
  }, [])

  useEffect(() => {
    refresh()
    const interval = setInterval(() => {
      // Only poll while something is still processing, to avoid needless traffic.
      setDocuments((current) => {
        if (current.some((d) => d.status === 'processing')) refresh()
        return current
      })
    }, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [refresh])

  function handleUploaded(doc) {
    setDocuments((prev) => [doc, ...prev])
    setActiveDoc(doc)
  }

  async function handleDelete(docId) {
    await deleteDocument(docId)
    setDocuments((prev) => prev.filter((d) => d.id !== docId))
    setActiveDoc((prev) => (prev?.id === docId ? null : prev))
  }

  return (
    <div className="app-shell">
      <DocumentList
        documents={documents}
        activeDocId={activeDoc?.id}
        onSelect={setActiveDoc}
        onDelete={handleDelete}
        onUploaded={handleUploaded}
      />
      <ChatWindow document={activeDoc} />
    </div>
  )
}
