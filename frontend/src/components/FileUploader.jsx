import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { documentsApi } from '../api/client'

const ACCEPTED_TYPES = ['.pdf', '.docx', '.txt', '.html', '.htm']
const ACCEPTED_MIME = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'text/html',
]

export default function FileUploader({ projectId, onUploadDone }) {
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const inputRef = useRef()

  const validateFile = (file) => {
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    if (!ACCEPTED_TYPES.includes(ext)) {
      return `Unsupported file type "${ext}". Accepted: ${ACCEPTED_TYPES.join(', ')}`
    }
    if (file.size > 50 * 1024 * 1024) {
      return 'File must be under 50MB'
    }
    return null
  }

  const handleFile = async (file) => {
    setError(null)
    const err = validateFile(file)
    if (err) { setError(err); return }

    setUploading(true)
    setProgress(0)

    try {
      const result = await documentsApi.upload(projectId, file, (pct) => setProgress(pct))
      if (onUploadDone) onUploadDone(result.document)
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const onInputChange = (e) => {
    const file = e.target.files[0]
    if (file) handleFile(file)
    e.target.value = ''
  }

  return (
    <div>
      <div
        className={`dropzone ${dragOver ? 'drag-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => !uploading && inputRef.current?.click()}
        style={{ cursor: uploading ? 'default' : 'pointer' }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES.join(',')}
          style={{ display: 'none' }}
          onChange={onInputChange}
          id="file-upload-input"
        />

        <AnimatePresence mode="wait">
          {uploading ? (
            <motion.div
              key="uploading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}
            >
              <div style={{ fontSize: '2rem' }}>⬆️</div>
              <p style={{ fontWeight: 700, color: 'var(--black)' }}>Uploading...</p>
              <div style={{
                width: '280px', height: 10,
                background: 'var(--gray-200)',
                border: '2px solid var(--black)',
                overflow: 'hidden',
              }}>
                <motion.div
                  style={{
                    height: '100%',
                    background: 'var(--black)',
                  }}
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.2 }}
                />
              </div>
              <p style={{ fontSize: '0.9375rem', color: 'var(--gray-500)', fontWeight: 600 }}>{progress}%</p>
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="dropzone-icon">{dragOver ? '📥' : '📄'}</div>
              <p style={{ fontWeight: 700, color: 'var(--black)', marginBottom: '0.375rem', fontSize: '1.125rem' }}>
                {dragOver ? 'Drop to upload!' : 'Drag & drop or click to upload'}
              </p>
              <p style={{ fontSize: '1rem', color: 'var(--gray-500)' }}>
                Supports: PDF, DOCX, TXT, HTML (max 50MB)
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{
              marginTop: '0.875rem',
              padding: '0.875rem 1.25rem',
              background: 'var(--white)',
              border: '2px solid var(--black)',
              color: 'var(--black)',
              fontSize: '1rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '0.625rem',
            }}
          >
            {error}
            <button
              style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--black)', fontWeight: 700, fontSize: '1.125rem' }}
              onClick={() => setError(null)}
            >
              ✕
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
