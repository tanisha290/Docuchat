const BASE_URL = '/api'

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.error || `Request failed with status ${res.status}`)
  }
  return data
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  })
  return handleResponse(res)
}

export async function listDocuments() {
  const res = await fetch(`${BASE_URL}/documents`)
  return handleResponse(res)
}

export async function deleteDocument(documentId) {
  const res = await fetch(`${BASE_URL}/documents/${documentId}`, { method: 'DELETE' })
  return handleResponse(res)
}

export async function createConversation(documentId) {
  const res = await fetch(`${BASE_URL}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId ?? null }),
  })
  return handleResponse(res)
}

export async function listConversations() {
  const res = await fetch(`${BASE_URL}/conversations`)
  return handleResponse(res)
}

export async function getConversation(conversationId) {
  const res = await fetch(`${BASE_URL}/conversations/${conversationId}`)
  return handleResponse(res)
}

export async function sendMessage(conversationId, content) {
  const res = await fetch(`${BASE_URL}/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return handleResponse(res)
}
