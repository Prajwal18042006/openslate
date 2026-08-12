import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { projectsApi, chatApi } from '../api/client'
import ChatWindow from '../components/ChatWindow'

export default function ChatPage() {
  const { projectId } = useParams()
  const [project, setProject] = useState(null)
  const [messages, setMessages] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [clearing, setClearing] = useState(false)
  const textareaRef = useRef()

  // -------------------------------------------------------
  // Load project + history
  // -------------------------------------------------------
  useEffect(() => {
    const load = async () => {
      try {
        const [proj, hist] = await Promise.all([
          projectsApi.getOne(projectId),
          chatApi.history(projectId),
        ])
        setProject(proj)

        // Convert history to display format (no sources for history)
        const msgs = (hist.messages || []).map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          created_at: m.created_at,
          sources: [],
        }))
        setMessages(msgs)
      } catch (e) {
        console.error(e)
      } finally {
        setLoadingHistory(false)
      }
    }
    load()
  }, [projectId])

  // -------------------------------------------------------
  // Send message
  // -------------------------------------------------------
  const sendMessage = async () => {
    const text = query.trim()
    if (!text || loading) return

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMsg])
    setQuery('')
    setLoading(true)

    // Resize textarea
    if (textareaRef.current) textareaRef.current.style.height = 'auto'

    try {
      const res = await chatApi.ask(text, projectId)

      const aiMsg = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        sources: res.sources || [],
        created_at: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, aiMsg])
    } catch (e) {
      const errMsg = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `❌ Error: ${e.message}`,
        sources: [],
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleTextareaChange = (e) => {
    setQuery(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
  }

  const handleClearHistory = async () => {
    if (!confirm('Clear all chat history?')) return
    setClearing(true)
    try {
      await chatApi.clearHistory(projectId)
      setMessages([])
    } finally {
      setClearing(false)
    }
  }

  // -------------------------------------------------------
  // Render
  // -------------------------------------------------------
  return (
    <div className="page">
      <header className="project-header" style={{ padding: '1.5rem 0' }}>
        <div className="container flex items-center justify-between gap-4" style={{ flexWrap: 'wrap' }}>
          <div className="flex items-center gap-4">
            <Link to={`/projects/${projectId}`} className="btn btn-ghost btn-sm">← Back</Link>
            <div>
              <p className="landing-eyebrow" style={{ marginBottom: '0.375rem' }}>RAG Chat</p>
              <h1 className="project-name" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.75rem)' }}>
                {project?.name || '…'}
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3" style={{ flexWrap: 'wrap' }}>
            {['MiniLM-L6', 'ChromaDB', 'Qwen2.5-VL'].map((label) => (
              <span key={label} className="detail-meta-tag">{label}</span>
            ))}
            {messages.length > 0 && (
              <button className="btn btn-ghost btn-sm" onClick={handleClearHistory} disabled={clearing}>
                {clearing ? <span className="spinner" /> : 'Clear history'}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {loadingHistory ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
            <span className="spinner spinner-lg" />
          </div>
        ) : (
          <ChatWindow messages={messages} loading={loading} />
        )}
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <div className="chat-input-row">
          <textarea
            ref={textareaRef}
            id="chat-query-input"
            className="chat-input"
            placeholder="Ask a question about your documents… (Enter to send, Shift+Enter for newline)"
            value={query}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={loading}
          />
          <button
            id="chat-send-btn"
            className="btn btn-primary"
            style={{ flexShrink: 0, alignSelf: 'flex-end' }}
            onClick={sendMessage}
            disabled={loading || !query.trim()}
          >
            {loading ? (
              <span className="spinner" />
            ) : (
              <>Send ↑</>
            )}
          </button>
        </div>

        <p style={{
          fontSize: '0.875rem', color: 'var(--gray-400)',
          textAlign: 'center', marginTop: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
        }}>
          Powered by RAG — retrieves from ChromaDB, answers with Qwen2.5-VL
        </p>
      </div>
    </div>
  )
}
