import { motion } from 'framer-motion'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const isAI = message.role === 'assistant'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        alignItems: 'flex-start',
        gap: '0.625rem',
      }}
    >
      {/* AI Avatar */}
      {isAI && (
        <div style={{
          width: 40, height: 40, flexShrink: 0,
          background: 'var(--black)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.875rem', color: 'white', fontWeight: 700,
          marginTop: '0.125rem',
          fontFamily: 'var(--font-heading)',
        }}>
          OS
        </div>
      )}

      {/* Bubble */}
      <div style={{ maxWidth: '72%', minWidth: 60 }}>
        <div style={{
          padding: '1rem 1.25rem',
          borderRadius: 0,
          background: isUser ? 'var(--black)' : 'var(--white)',
          color: isUser ? 'white' : 'var(--black)',
          border: isUser ? '2px solid var(--black)' : '2px solid var(--black)',
          fontSize: '1.0625rem',
          lineHeight: 1.7,
          wordBreak: 'break-word',
          whiteSpace: 'pre-wrap',
        }}>
          {message.content}
        </div>

        {/* Sources */}
        {isAI && message.sources && message.sources.length > 0 && (
          <div style={{ marginTop: '0.625rem' }}>
            <p style={{
              fontSize: '0.8125rem', fontWeight: 700, textTransform: 'uppercase',
              letterSpacing: '0.08em', color: 'var(--gray-500)', marginBottom: '0.5rem',
            }}>
              📚 Sources ({message.sources.length})
            </p>
            {message.sources.map((source, i) => (
              <div key={i} className="source-card">
                <div className="source-card-header">
                  <span>📌 Source {i + 1}</span>
                  {source.metadata?.filename && (
                    <span style={{ color: 'var(--gray-400)' }}>
                      {source.metadata.filename}
                    </span>
                  )}
                  {source.metadata?.page_number && (
                    <span style={{
                      marginLeft: 'auto',
                      background: 'var(--black)',
                      color: 'var(--white)',
                      padding: '0.15rem 0.5rem',
                      fontSize: '0.8125rem',
                      fontWeight: 700,
                    }}>
                      p.{source.metadata.page_number}
                    </span>
                  )}
                </div>
                <p style={{
                  fontSize: '1rem', color: 'var(--gray-600)',
                  lineHeight: 1.65,
                  display: '-webkit-box',
                  WebkitLineClamp: 4,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}>
                  {source.content}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        {message.created_at && (
          <p style={{
            fontSize: '0.8125rem', color: 'var(--gray-400)',
            marginTop: '0.375rem',
            textAlign: isUser ? 'right' : 'left',
          }}>
            {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div style={{
          width: 40, height: 40, flexShrink: 0,
          background: 'var(--white)',
          border: '2px solid var(--black)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1rem', marginTop: '0.125rem',
        }}>
          👤
        </div>
      )}
    </motion.div>
  )
}
