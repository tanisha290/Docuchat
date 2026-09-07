import { useRef, useState } from 'react'
import { uploadDocument } from '../api/client'

export default function UploadButton({ onUploaded }) {
  const inputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  async function handleChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setError(null)
    setUploading(true)
    try {
      const { document } = await uploadDocument(file)
      onUploaded(document)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  return (
    <div className="upload-area">
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        style={{ display: 'none' }}
        onChange={handleChange}
      />
      <button
        className="upload-btn"
        disabled={uploading}
        onClick={() => inputRef.current?.click()}
      >
        {uploading ? 'Processing…' : 'Upload PDF'}
      </button>
      <div className="upload-hint">PDF files up to 25MB</div>
      {error && <div className="upload-error">{error}</div>}
    </div>
  )
}
