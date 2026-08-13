import axios from 'axios'

// =========================================================
// API Configuration
// =========================================================

// Production Backend
const API_BASE_URL =
  'http://127.0.0.1:8000/api'

// Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 220000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// =========================================================
// Response Interceptor
// =========================================================

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg =
      err.response?.data?.detail ||
      err.message ||
      'Something went wrong'

    return Promise.reject(new Error(msg))
  }
)

// =========================================================
// PROJECTS
// =========================================================

export const projectsApi = {
  getAll: () =>
    api.get('/projects/').then((r) => r.data),

  getOne: (id) =>
    api.get(`/projects/${id}`).then((r) => r.data),

  create: (data) =>
    api.post('/projects/', data).then((r) => r.data),

  delete: (id) =>
    api.delete(`/projects/${id}`).then((r) => r.data),
}

// =========================================================
// DOCUMENTS
// =========================================================

export const documentsApi = {
  getByProject: (projectId) =>
    api
      .get(`/documents/project/${projectId}`)
      .then((r) => r.data),

  getOne: (id) =>
    api
      .get(`/documents/${id}`)
      .then((r) => r.data),

  upload: (projectId, file, onProgress) => {
    const formData = new FormData()

    formData.append('file', file)
    formData.append('project_id', projectId)

    return api
      .post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },

        onUploadProgress: (e) => {
          if (e.total) {
            const pct = Math.round(
              (e.loaded * 100) / e.total
            )

            if (onProgress) {
              onProgress(pct)
            }
          }
        },
      })
      .then((r) => r.data)
  },

  delete: (id) =>
    api
      .delete(`/documents/${id}`)
      .then((r) => r.data),
}

// =========================================================
// PIPELINE
// =========================================================

export const pipelineApi = {
  process: (documentId) =>
    api
      .post(`/pipeline/process/${documentId}`)
      .then((r) => r.data),

  status: (documentId) =>
    api
      .get(`/pipeline/status/${documentId}`)
      .then((r) => r.data),
}

// =========================================================
// CHUNKS
// =========================================================

export const chunksApi = {
  getByDocument: (documentId, q = '') => {
    const params = q ? { q } : {}

    return api
      .get(`/documents/${documentId}/chunks`, {
        params,
      })
      .then((r) => r.data)
  },

  getOne: (documentId, chunkId) =>
    api
      .get(
        `/documents/${documentId}/chunks/${chunkId}`
      )
      .then((r) => r.data),
}

// =========================================================
// CHAT
// =========================================================

export const chatApi = {
  ask: (query, projectId) =>
    api
      .post('/chat/ask', {
        query,
        project_id: projectId,
      })
      .then((r) => r.data),

  history: (projectId) =>
    api
      .get(`/chat/history/${projectId}`)
      .then((r) => r.data),

  clearHistory: (projectId) =>
    api
      .delete(`/chat/history/${projectId}`)
      .then((r) => r.data),
}

// =========================================================
// HEALTH
// =========================================================

export const healthApi = {
  check: () =>
    api
      .get('/health')
      .then((r) => r.data),
}

// =========================================================
// Default Export
// =========================================================

export default api