import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { pipelineApi } from '../api/client'

// Pipeline stages definition
const STAGES = [
  {
    key: 'extract',
    icon: '📄',
    label: 'Extract',
    description: 'Parse document structure, text, tables, and images',
    color: '#000000',
  },
  {
    key: 'chunk',
    icon: '✂️',
    label: 'Chunk',
    description: 'Semantic chunking by title/section (max 3000 chars)',
    color: '#404040',
  },
  {
    key: 'summarize',
    icon: '🧠',
    label: 'Summarize',
    description: 'AI-enhanced searchable summaries via VLM',
    color: '#525252',
  },
  {
    key: 'embed',
    icon: '🔢',
    label: 'Embed',
    description: 'Generate 384-dim vectors via sentence-transformers',
    color: '#737373',
  },
  {
    key: 'store',
    icon: '🗄️',
    label: 'VectorStore',
    description: 'Persist embeddings in ChromaDB for retrieval',
    color: '#000000',
  },
]

const STATUS_STAGE_MAP = {
  extracting: 'extract',
  chunking: 'chunk',
  summarizing: 'summarize',
  embedding: 'embed',
  storing: 'store',
  ready: '__done__',
  error: '__error__',
}

function StepStats({ stepKey, data }) {
  if (!data) return null

  const items = Object.entries(data).filter(([k]) => k !== 'status')

  if (items.length === 0) return null

  return (
    <div style={{
      marginTop: '0.5rem',
      display: 'flex', flexWrap: 'wrap', gap: '0.5rem',
    }}>
      {items.map(([k, v]) => (
        <span key={k} style={{
          background: 'var(--white)',
          border: '2px solid var(--black)',
          padding: '0.25rem 0.75rem',
          fontSize: '0.8125rem',
          fontWeight: 700,
          color: 'var(--black)',
        }}>
          {k.replace(/_/g, ' ')}: {Array.isArray(v) ? v.join(', ') : String(v)}
        </span>
      ))}
    </div>
  )
}

export default function PipelineStatus({ documentId, filename, onComplete }) {
  const [running, setRunning] = useState(false)
  const [activeStage, setActiveStage] = useState(null)
  const [completedStages, setCompletedStages] = useState([])
  const [stageData, setStageData] = useState({})
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [elapsed, setElapsed] = useState(0)

  const getStageStatus = (stageKey) => {
    if (completedStages.includes(stageKey)) return 'done'
    if (activeStage === stageKey) return 'active'
    return 'pending'
  }

  const runPipeline = async () => {
    setRunning(true)
    setError(null)
    setResult(null)
    setCompletedStages([])
    setStageData({})
    setActiveStage('extract')

    const startTime = Date.now()
    const timer = setInterval(() => {
      setElapsed(Math.round((Date.now() - startTime) / 1000))
    }, 1000)

    try {
      const res = await pipelineApi.process(documentId)

      // Mark all stages done
      setActiveStage(null)
      setCompletedStages(STAGES.map((s) => s.key))
      setStageData(res.steps || {})
      setResult(res)

      if (onComplete) onComplete(res)
    } catch (e) {
      setError(e.message)
      setActiveStage(null)
    } finally {
      setRunning(false)
      clearInterval(timer)
    }
  }

  const allDone = completedStages.length === STAGES.length

  return (
    <div>
      {/* Stage Flow */}
      <div className="pipeline-flow" style={{ gap: '0', marginBottom: '1.5rem' }}>
        {STAGES.map((stage, i) => {
          const status = getStageStatus(stage.key)
          return (
            <div key={stage.key} style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              {/* Step */}
              <motion.div
                className={`pipeline-step ${status}`}
                style={{ flex: 'none' }}
                animate={status === 'active' ? { scale: [1, 1.05, 1] } : {}}
                transition={{ repeat: Infinity, duration: 1 }}
              >
                <div
                  className="pipeline-step-icon"
                  style={status === 'done' ? {
                    background: stage.color,
                    borderColor: stage.color,
                    color: 'white',
                  } : status === 'active' ? {
                    borderColor: stage.color,
                    background: `${stage.color}15`,
                  } : {}}
                >
                  {status === 'done' ? '✓' : stage.icon}
                </div>
                <span className="pipeline-step-label">{stage.label}</span>
              </motion.div>

              {/* Connector */}
              {i < STAGES.length - 1 && (
                <div
                  className={`pipeline-connector ${completedStages.includes(stage.key) ? 'done' : ''}`}
                />
              )}
            </div>
          )
        })}
      </div>

      {/* Stage Details (when running or done) */}
      <AnimatePresence>
        {(running || allDone || error) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{ overflow: 'hidden', marginBottom: '1.25rem' }}
          >
            <div style={{
              background: 'var(--white)',
              border: '2px solid var(--black)',
              padding: '1.25rem',
            }}>
              {STAGES.map((stage) => {
                const status = getStageStatus(stage.key)
                if (status === 'pending' && !allDone) return null
                return (
                  <div key={stage.key} style={{
                    display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                    padding: '0.5rem 0',
                    borderBottom: '1px solid var(--gray-100)',
                    opacity: status === 'pending' ? 0.4 : 1,
                  }}>
                    <span style={{ fontSize: '1rem', marginTop: '0.1rem' }}>
                      {status === 'done' ? '✅' : status === 'active' ? '⏳' : '⬜'}
                    </span>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{stage.label}</span>
                        {status === 'active' && (
                          <span className="spinner" style={{ width: 12, height: 12 }} />
                        )}
                      </div>
                      <p style={{ fontSize: '0.7875rem', color: 'var(--gray-500)', marginTop: '0.1rem' }}>
                        {stage.description}
                      </p>
                      <StepStats stepKey={stage.key} data={stageData[stage.key]} />
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Run Button / Status */}
      {!allDone && !error && (
        <button
          id={`run-pipeline-${documentId}`}
          className="btn btn-primary"
          onClick={runPipeline}
          disabled={running}
        >
          {running ? (
            <>
              <span className="spinner" />
              Processing... ({elapsed}s)
            </>
          ) : (
            '▶ Run Pipeline'
          )}
        </button>
      )}

      {/* Success Result */}
      <AnimatePresence>
        {allDone && result && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              display: 'flex', alignItems: 'center', gap: '0.875rem',
              padding: '1rem 1.25rem',
              background: 'var(--white)',
              border: '2px solid var(--black)',
            }}
          >
            <span style={{ fontSize: '1.5rem' }}>✓</span>
            <div>
              <p style={{ fontWeight: 700, color: 'var(--black)', fontSize: '1.0625rem' }}>
                Pipeline completed!
              </p>
              <p style={{ fontSize: '1rem', color: 'var(--gray-500)' }}>
                Ready for RAG chat • {elapsed}s elapsed
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              display: 'flex', alignItems: 'flex-start', gap: '0.875rem',
              padding: '1rem 1.25rem',
              background: 'var(--white)',
              border: '2px solid var(--black)',
            }}
          >
            <span>✕</span>
            <div style={{ flex: 1 }}>
              <p style={{ fontWeight: 700, color: 'var(--black)', fontSize: '1rem' }}>Pipeline failed</p>
              <p style={{ fontSize: '0.9375rem', color: 'var(--gray-600)', marginTop: '0.375rem' }}>{error}</p>
            </div>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => { setError(null); setCompletedStages([]); setActiveStage(null) }}
            >
              Retry
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
