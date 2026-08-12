import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { pipelineApi, chunksApi } from '../api/client'
import DetailInspector from './DetailInspector'

const STAGES = [
  { key: 'upload', label: 'Upload', title: 'Upload', desc: 'Document uploaded and queued for processing' },
  { key: 'extract', label: 'Extract', title: 'Extracting', desc: 'Parsing document structure, text, tables, and images' },
  { key: 'chunk', label: 'Chunking', title: 'Chunking', desc: 'Semantic chunking by title and section boundaries' },
  { key: 'summarize', label: 'Summarisation', title: 'Summarisation', desc: 'Enhancing content with AI summaries for images and tables' },
  { key: 'embed', label: 'Vectorization', title: 'Vectorization', desc: 'Generating 384-dimensional embeddings via MiniLM' },
  { key: 'store', label: 'Storage', title: 'Vector Store', desc: 'Persisting embeddings in ChromaDB for retrieval' },
  { key: 'chunks', label: 'View Chunks', title: 'Document Chunks', desc: 'Browse all processed chunks for this document' },
]

const STATUS_TO_STAGE = {
  uploaded: 'upload',
  extracting: 'extract',
  chunking: 'chunk',
  summarizing: 'summarize',
  embedding: 'embed',
  storing: 'store',
  ready: 'chunks',
  error: 'extract',
}

function getProgress(stageKey, stepData, chunksTotal, running) {
  if (stageKey === 'upload') return { current: 1, total: 1, label: 'uploaded' }
  if (stageKey === 'chunks') return { current: chunksTotal, total: chunksTotal || 0, label: 'chunks indexed' }

  const data = stepData?.[stageKey]
  if (!data) return running ? { current: 0, total: 1, label: 'processing' } : null

  if (stageKey === 'chunk') {
    const n = data.total_chunks || 0
    return { current: n, total: n, label: 'chunks created' }
  }
  if (stageKey === 'summarize') {
    const n = data.processed || 0
    return { current: n, total: n, label: 'chunks processed' }
  }
  if (stageKey === 'extract') {
    return { current: data.elements || 0, total: data.elements || 0, label: 'elements extracted' }
  }
  if (stageKey === 'embed') {
    return { current: 384, total: 384, label: 'dimensions' }
  }
  if (stageKey === 'store') {
    const n = data.vectors_stored || 0
    return { current: n, total: n, label: 'vectors stored' }
  }
  return null
}

export default function PipelineWorkspace({ documentId, filename, status, onComplete, onStatusChange }) {
  const [activeTab, setActiveTab] = useState(STATUS_TO_STAGE[status] || 'upload')
  const [running, setRunning] = useState(false)
  const [stepData, setStepData] = useState({})
  const [error, setError] = useState(null)
  const [elapsed, setElapsed] = useState(0)
  const [chunks, setChunks] = useState([])
  const [selectedChunk, setSelectedChunk] = useState(null)
  const [chunkSearch, setChunkSearch] = useState('')
  const [loadingChunks, setLoadingChunks] = useState(false)

  useEffect(() => {
    if (status) setActiveTab(STATUS_TO_STAGE[status] || 'upload')
  }, [status])

  const loadChunks = async (search = '') => {
    if (!documentId) return
    setLoadingChunks(true)
    try {
      const data = await chunksApi.getByDocument(documentId, search)
      setChunks(data.chunks || [])
      if (data.chunks?.length && !selectedChunk) {
        setSelectedChunk(data.chunks[0])
      }
    } catch {
      setChunks([])
    } finally {
      setLoadingChunks(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'chunks' || status === 'ready') {
      loadChunks(chunkSearch)
    }
  }, [activeTab, documentId, status])

  const runPipeline = async () => {
    setRunning(true)
    setError(null)
    setStepData({})
    setActiveTab('extract')
    if (onStatusChange) onStatusChange('extracting')

    const start = Date.now()
    const timer = setInterval(() => setElapsed(Math.round((Date.now() - start) / 1000)), 1000)

    try {
      const res = await pipelineApi.process(documentId)
      setStepData(res.steps || {})
      setActiveTab('chunks')
      if (onComplete) onComplete(res)
      await loadChunks()
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
      clearInterval(timer)
    }
  }

  const stage = STAGES.find((s) => s.key === activeTab) || STAGES[0]
  const progress = getProgress(activeTab, stepData, chunks.length, running)
  const pct = progress && progress.total > 0
    ? Math.round((progress.current / progress.total) * 100)
    : running ? 50 : (status === 'ready' ? 100 : 0)

  const inspectorContent = activeTab === 'chunks' && selectedChunk
    ? {
        title: `Chunk #${(selectedChunk.index ?? 0) + 1}`,
        meta: [
          selectedChunk.type && `Type: ${selectedChunk.type}`,
          selectedChunk.page_number != null && `Page ${selectedChunk.page_number}`,
          `${selectedChunk.char_count} chars`,
        ].filter(Boolean),
        body: selectedChunk.content,
      }
    : progress
      ? {
          title: stage.title,
          meta: [filename, status].filter(Boolean),
          body: stage.desc + (progress.total > 0
            ? `\n\nProgress: ${progress.current} / ${progress.total} ${progress.label}`
            : ''),
          stats: stepData[activeTab] ? Object.entries(stepData[activeTab])
            .filter(([k]) => k !== 'status')
            .map(([k, v]) => `${k.replace(/_/g, ' ')}: ${Array.isArray(v) ? v.join(', ') : v}`)
            : [],
        }
      : {
          title: stage.title,
          meta: [filename],
          body: stage.desc,
        }

  return (
    <div className="pipeline-workspace">
      <div className="pipeline-tabs">
        {STAGES.map((s) => (
          <button
            key={s.key}
            type="button"
            className={`pipeline-tab ${activeTab === s.key ? 'active' : ''}`}
            onClick={() => setActiveTab(s.key)}
          >
            {s.label}
          </button>
        ))}
      </div>

      <div className="pipeline-layout">
        <div className="pipeline-main">
          <h3 className="pipeline-stage-title">{stage.title}</h3>
          <p className="pipeline-stage-desc">{stage.desc}</p>

          {activeTab === 'chunks' ? (
            <div>
              <div className="chunks-search">
                <input
                  className="form-input w-full"
                  placeholder="Search chunks..."
                  value={chunkSearch}
                  onChange={(e) => setChunkSearch(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && loadChunks(chunkSearch)}
                />
              </div>

              {loadingChunks ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                  <span className="spinner spinner-lg" />
                </div>
              ) : chunks.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-state-icon">📄</div>
                  <h3>No chunks yet</h3>
                  <p>Run the pipeline to extract and index document chunks</p>
                  {status !== 'ready' && (
                    <button className="btn btn-primary" onClick={runPipeline} disabled={running}>
                      {running ? <><span className="spinner" /> Processing...</> : '▶ Run Pipeline'}
                    </button>
                  )}
                </div>
              ) : (
                <div className="chunks-list">
                  {chunks.map((chunk) => (
                    <button
                      key={chunk.id}
                      type="button"
                      className={`chunk-row ${selectedChunk?.id === chunk.id ? 'selected' : ''}`}
                      onClick={() => setSelectedChunk(chunk)}
                    >
                      <span className="chunk-index">{(chunk.index ?? 0) + 1}</span>
                      <div className="chunk-preview">
                        <div className="chunk-preview-title">
                          {chunk.type} {chunk.page_number != null && `· Page ${chunk.page_number}`}
                          {' · '}{chunk.char_count} chars
                        </div>
                        <div className="chunk-preview-text">{chunk.content}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <>
              <div className="progress-card">
                <div className="progress-card-label">
                  {running ? '⏳ Processing...' : status === 'ready' ? '✓ Complete' : 'Pipeline Progress'}
                </div>
                {progress ? (
                  <>
                    <div className="progress-big">
                      {progress.current} / {progress.total}
                    </div>
                    <div className="progress-sub">{progress.label}</div>
                  </>
                ) : (
                  <>
                    <div className="progress-big">{running ? '...' : '—'}</div>
                    <div className="progress-sub">
                      {running ? `Elapsed ${elapsed}s` : 'Ready to process'}
                    </div>
                  </>
                )}
                <div className="progress-bar-wrap">
                  <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
                </div>
                <p className="progress-note">
                  {running
                    ? 'Processing chunks and creating AI summaries for images and tables.'
                    : status === 'ready'
                      ? 'All pipeline stages completed successfully.'
                      : 'Select Run Pipeline to start document processing.'}
                </p>
              </div>

              {status !== 'ready' && !running && (
                <div style={{ marginTop: '1.25rem' }}>
                  <button className="btn btn-primary btn-lg" onClick={runPipeline} disabled={running}>
                    ▶ Run Pipeline
                  </button>
                </div>
              )}

              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  style={{
                    marginTop: '1rem', padding: '1rem',
                    background: 'var(--gray-50)', border: '1px solid var(--black)',
                    borderRadius: 'var(--radius-md)', fontWeight: 600,
                  }}
                >
                  Pipeline failed: {error}
                </motion.div>
              )}
            </>
          )}
        </div>

        <DetailInspector
          title="Detail Inspector"
          content={inspectorContent}
        />
      </div>
    </div>
  )
}
