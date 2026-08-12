import { motion, AnimatePresence } from 'framer-motion'
import { documentsApi } from '../api/client'
import { useState } from 'react'

const STATUS_LABELS = {
  uploaded: 'Uploaded',
  extracting: 'Extracting',
  chunking: 'Chunking',
  summarizing: 'Summarizing',
  embedding: 'Embedding',
  storing: 'Storing',
  ready: 'Ready',
  error: 'Error',
}

const FILE_ICONS = {
  pdf: '📕',
  docx: '📘',
  txt: '📝',
  html: '🌐',
  htm: '🌐',
}

function getFileIcon(filename) {
  const ext = filename?.split('.').pop()?.toLowerCase()
  return FILE_ICONS[ext] || '📄'
}

function StatusBadge({ status }) {
  return (
    <span className={`badge badge-${status}`}>
      <span className="badge-dot" />
      {STATUS_LABELS[status] || status}
    </span>
  )
}

function DocumentRow({ doc, onDelete, onRunPipeline, activeDocId }) {
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async () => {
    if (!confirm(`Remove "${doc.filename}"?`)) return
    setDeleting(true)
    try {
      await documentsApi.delete(doc.id)
      onDelete(doc.id)
    } finally {
      setDeleting(false)
    }
  }

  const isProcessing = ['extracting', 'chunking', 'summarizing', 'embedding', 'storing'].includes(doc.status)

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 10 }}
      className={`doc-row ${activeDocId === doc.id ? 'active' : ''}`}
      onClick={() => onRunPipeline(doc)}
    >
      {/* Icon */}
      <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>
        {getFileIcon(doc.filename)}
      </span>

      {/* Info */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <p className="doc-row-name">{doc.filename}</p>
        <p className="doc-row-meta">
          ID: {doc.id.slice(0, 8)}… •{' '}
          {doc.created_at ? new Date(doc.created_at).toLocaleString() : '—'}
        </p>
      </div>

      {/* Status */}
      <StatusBadge status={doc.status} />

      {/* Actions */}
      <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
        {doc.status === 'uploaded' && (
          <button
            className="btn btn-primary btn-sm"
            onClick={(e) => { e.stopPropagation(); onRunPipeline(doc) }}
          >
            ▶ Process
          </button>
        )}
        {doc.status === 'ready' && (
          <span style={{ fontSize: '0.9375rem', color: 'var(--black)', fontWeight: 700 }}>
            Ready
          </span>
        )}
        {isProcessing && (
          <span className="spinner" style={{ width: 16, height: 16 }} />
        )}
        <button
          className="btn btn-danger btn-sm btn-icon"
          onClick={(e) => { e.stopPropagation(); handleDelete() }}
          disabled={deleting || isProcessing}
          title="Remove document"
        >
          {deleting ? <span className="spinner" style={{ width: 12, height: 12 }} /> : '🗑'}
        </button>
      </div>
    </motion.div>
  )
}

export default function SourceList({ documents, onDelete, onRunPipeline, activeDocId }) {
  if (!documents || documents.length === 0) {
    return (
      <div style={{
        padding: '2.5rem', textAlign: 'center',
        background: 'var(--white)',
        border: '2px dashed var(--black)',
      }}>
        <span style={{ fontSize: '2.5rem' }}>—</span>
        <p style={{ marginTop: '0.75rem', color: 'var(--gray-500)', fontSize: '1.0625rem', fontWeight: 600 }}>
          No documents yet — upload a file above
        </p>
      </div>
    )
  }

  const readyCount = documents.filter((d) => d.status === 'ready').length

  return (
    <div>
      {/* Summary */}
      {readyCount > 0 && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.625rem',
          padding: '0.75rem 1rem',
          background: 'var(--black)',
          border: '2px solid var(--black)',
          marginBottom: '0.875rem',
          fontSize: '0.9375rem', fontWeight: 700, color: 'var(--white)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
        }}>
          {readyCount} of {documents.length} document{documents.length !== 1 ? 's' : ''} indexed and ready for chat
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <AnimatePresence>
          {documents.map((doc) => (
            <DocumentRow
              key={doc.id}
              doc={doc}
              onDelete={onDelete}
              onRunPipeline={onRunPipeline}
              activeDocId={activeDocId}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}
