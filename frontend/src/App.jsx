import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import ChatPage from './pages/ChatPage'
import Watermark from './components/Watermark'
import Footer from './components/Footer'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return null
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function Navbar() {
  const location = useLocation()
  const { user, logout } = useAuth()

  if (location.pathname === '/login') return null

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <span className="navbar-brand-dot"></span>
        OpenSlate
      </Link>
      <div className="navbar-links">
        <Link
          to="/"
          className={`navbar-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          Projects
        </Link>
        <a
          href="http://localhost:8000/api/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="navbar-link"
        >
          API Docs
        </a>
        {user && <span className="navbar-user">{user.name}</span>}
        <button type="button" className="btn btn-ghost btn-sm" onClick={logout}>
          Logout
        </button>
      </div>
    </nav>
  )
}

function AppRoutes() {
  return (
    <div className="app-shell">
      <Watermark />
      <Navbar />
      <main className="app-main">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
          <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
          <Route path="/projects/:projectId/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
