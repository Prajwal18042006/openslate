import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { projectsApi, documentsApi } from '../api/client'
import FileUploader from '../components/FileUploader'
import SourceList from '../components/SourceList'
import PipelineWorkspace from '../components/PipelineWorkspace'

function Toast({ message, type, onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500)
    return () => clearTimeout(t)
  }, [onClose])
  return (
    <motion.div className={`toast toast-${type}`} initial={{ opacity: 0, x: 60 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 60 }}>
      {type === 'success' ? '✓' : '✕'} {message}
    </motion.div>
  )
}

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const [project, setProject] = useState(null)
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeDoc, setActiveDoc] = useState(null)
  const [toasts, setToasts] = useState([])

  const addToast = (message, type = 'success') => setToasts((t) => [...t, { id: Date.now(), message, type }])
  const removeToast = (id) => setToasts((t) => t.filter((x) => x.id !== id))

  const loadData = async () => {
    try {
      const [projectData, docsData] = await Promise.all([
        projectsApi.getOne(projectId),
        documentsApi.getByProject(projectId),
      ])
      setProject(projectData)
      const docs = docsData.documents || []
      setDocuments(docs)
      if (!activeDoc && docs.length > 0) setActiveDoc(docs[0])
    } catch (e) {
      addToast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [projectId])

  const handleUploadDone = (doc) => {
    setDocuments((prev) => [doc, ...prev])
    setActiveDoc(doc)
    addToast(`"${doc.filename}" uploaded!`)
  }

  const handleDocDelete = (docId) => {
    setDocuments((prev) => prev.filter((d) => d.id !== docId))
    if (activeDoc?.id === docId) setActiveDoc(null)
    addToast('Document removed')
  }

  const handlePipelineComplete = () => {
    setDocuments((prev) => prev.map((d) => d.id === activeDoc?.id ? { ...d, status: 'ready' } : d))
    setActiveDoc((d) => d ? { ...d, status: 'ready' } : d)
    addToast('Pipeline complete! View chunks in the Chunks tab.')
  }

  const readyCount = documents.filter((d) => d.status === 'ready').length

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <span className="spinner spinner-lg" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="container" style={{ padding: '4rem', textAlign: 'center' }}>
        <h2>Project not found</h2>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '1.25rem' }}>← Back</Link>
      </div>
    )
  }

  return (
    <div className="page">
      <header className="project-header">
        <div className="container">
          <nav className="project-breadcrumb">
            <Link to="/">Projects</Link>
            <span className="project-breadcrumb-sep">›</span>
            <span className="project-breadcrumb-current">{project.name}</span>
          </nav>

          <div className="project-header-row">
            <div>
              <h1 className="project-name">{project.name}</h1>
              {project.description && <p className="project-desc">{project.description}</p>}
            </div>
            {readyCount > 0 && (
              <Link to={`/projects/${projectId}/chat`} className="btn btn-primary btn-lg">
                Chat with Docs →
              </Link>
            )}
          </div>

          <div className="project-stats">
            {[
              { label: 'Documents', value: documents.length },
              { label: 'Ready', value: readyCount },
              { label: 'Processing', value: documents.length - readyCount },
            ].map(({ label, value }) => (
              <div key={label}>
                <div className="project-stat-value">{value}</div>
                <div className="project-stat-label">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      <div className="container project-layout">
        <aside className="project-sidebar">
          <motion.div className="card" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <h3 className="section-title" style={{ marginBottom: '1.25rem' }}>Upload</h3>
            <FileUploader projectId={projectId} onUploadDone={handleUploadDone} />
          </motion.div>

          <motion.div className="card" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
            <div className="section-header" style={{ marginBottom: '1rem' }}>
              <h3 className="section-title">Documents</h3>
              <span className="text-muted" style={{ fontWeight: 600 }}>{documents.length}</span>
            </div>
            <SourceList
              documents={documents}
              onDelete={handleDocDelete}
              onRunPipeline={setActiveDoc}
              activeDocId={activeDoc?.id}
            />
          </motion.div>
        </aside>

        <main className="project-main">
          <motion.div className="panel" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <div className="panel-header">
              <h3 className="section-title">Processing Pipeline</h3>
              {activeDoc && (
                <p className="section-subtitle" style={{ marginTop: '0.375rem' }}>{activeDoc.filename}</p>
              )}
            </div>
            <div className="panel-body">
              {activeDoc ? (
                <PipelineWorkspace
                  key={activeDoc.id}
                  documentId={activeDoc.id}
                  filename={activeDoc.filename}
                  status={activeDoc.status}
                  onComplete={handlePipelineComplete}
                  onStatusChange={(s) => setActiveDoc((d) => ({ ...d, status: s }))}
                />
              ) : (
                <div className="empty-state">
                  <div className="empty-state-icon">⚙</div>
                  <h3>Select a document</h3>
                  <p>Upload or select a document to view the pipeline and chunks</p>
                </div>
              )}
            </div>
          </motion.div>
        </main>
      </div>

      <div className="toast-container">
        <AnimatePresence>
          {toasts.map((t) => (
            <Toast key={t.id} message={t.message} type={t.type} onClose={() => removeToast(t.id)} />
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}
