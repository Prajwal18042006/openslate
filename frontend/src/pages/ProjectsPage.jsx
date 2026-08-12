import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { projectsApi } from '../api/client'

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

function ProjectCard({ project, onDelete, onClick }) {
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async (e) => {
    e.stopPropagation()
    if (!confirm(`Delete "${project.name}"?`)) return
    setDeleting(true)
    try { await onDelete(project.id) } finally { setDeleting(false) }
  }

  const dateStr = project.created_at
    ? new Date(project.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    : '—'

  return (
    <motion.div className="card" style={{ cursor: 'pointer' }} onClick={onClick} whileHover={{ y: -4 }}>
      <div className="flex items-center justify-between mb-4">
        <div className="project-card-icon">📁</div>
        <button className="btn btn-ghost btn-sm btn-icon" onClick={handleDelete} disabled={deleting}>✕</button>
      </div>
      <h3 className="project-card-title">{project.name}</h3>
      {project.description && (
        <p style={{ fontSize: '1rem', color: 'var(--gray-500)', marginBottom: '1.25rem',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {project.description}
        </p>
      )}
      <div className="divider" />
      <div className="flex items-center justify-between">
        <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--gray-500)' }}>
          {project.document_count ?? 0} documents
        </span>
        <span style={{ fontSize: '0.9375rem', color: 'var(--gray-400)' }}>{dateStr}</span>
      </div>
    </motion.div>
  )
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)
  const [toasts, setToasts] = useState([])
  const navigate = useNavigate()

  const addToast = (message, type = 'success') => setToasts((t) => [...t, { id: Date.now(), message, type }])
  const removeToast = (id) => setToasts((t) => t.filter((x) => x.id !== id))

  const load = async () => {
    setLoading(true)
    try {
      const data = await projectsApi.getAll()
      setProjects(data.projects || [])
    } catch (e) {
      addToast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!name.trim()) return
    setCreating(true)
    try {
      const res = await projectsApi.create({ name: name.trim(), description: description.trim() })
      addToast('Project created!')
      setName('')
      setDescription('')
      await load()
      if (res?.project?.id) navigate(`/projects/${res.project.id}`)
    } catch (err) {
      addToast(err.message, 'error')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await projectsApi.delete(id)
      addToast('Project deleted')
      setProjects((p) => p.filter((x) => x.id !== id))
    } catch (e) {
      addToast(e.message, 'error')
    }
  }

  return (
    <div className="page">
      <section className="landing-hero">
        <div className="container landing-hero-inner">
          <motion.div className="landing-intro" initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }}>
            <p className="landing-eyebrow">Document Intelligence</p>
            <h1 className="landing-title">OpenSlate</h1>
            <p className="landing-subtitle">
              Build knowledge bases from your documents. Extract, chunk, summarize, embed, and chat — all in one place.
            </p>
          </motion.div>

          <motion.div className="create-project-panel" initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <h2>Create Project</h2>
            <p>Name your project and start uploading documents</p>

            <form className="create-form" onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Project Name</label>
                <input
                  id="project-name"
                  className="form-input"
                  placeholder="e.g. Research Papers 2024"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Description (optional)</label>
                <textarea
                  className="form-textarea"
                  placeholder="What is this project about?"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
              <button type="submit" className="btn btn-primary btn-lg" disabled={creating || !name.trim()} style={{ alignSelf: 'flex-start' }}>
                {creating ? <span className="spinner" /> : 'Create Project →'}
              </button>
            </form>

            <div className="structure-steps">
              {[
                { n: 1, title: 'Upload', desc: 'Add PDF, DOCX, TXT files' },
                { n: 2, title: 'Process', desc: 'Run the RAG pipeline' },
                { n: 3, title: 'Chat', desc: 'Ask questions on your docs' },
              ].map(({ n, title, desc }) => (
                <div key={n} className="structure-step">
                  <div className="structure-step-num">{n}</div>
                  <strong>{title}</strong>
                  <span>{desc}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      <section className="container" style={{ padding: 'clamp(2.5rem, 6vw, 4rem) 0' }}>
        <div className="section-header">
          <div>
            <h2>Your Projects</h2>
            <p className="section-subtitle">{projects.length} project{projects.length !== 1 ? 's' : ''}</p>
          </div>
        </div>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '5rem' }}>
            <span className="spinner spinner-lg" />
          </div>
        ) : projects.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📂</div>
            <h3>No projects yet</h3>
            <p>Use the form above to create your first project</p>
          </div>
        ) : (
          <div className="project-grid">
            {projects.map((project, i) => (
              <motion.div key={project.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
                <ProjectCard project={project} onDelete={handleDelete} onClick={() => navigate(`/projects/${project.id}`)} />
              </motion.div>
            ))}
          </div>
        )}
      </section>

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
