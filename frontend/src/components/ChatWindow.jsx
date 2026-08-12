import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import MessageBubble from './MessageBubble'

export default function ChatWindow({ messages, loading }) {
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  if (messages.length === 0 && !loading) {
    return (
      <div className="chat-messages" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          style={{ textAlign: 'center', padding: '2rem' }}
        >
          <div style={{
            width: 96, height: 96,
            background: 'var(--white)',
            border: '2px solid var(--black)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '3rem', margin: '0 auto 1.25rem',
          }}>
            💬
          </div>
          <h3 style={{ fontFamily: 'var(--font-heading)', marginBottom: '0.625rem', fontSize: '1.75rem' }}>
            Ask your documents anything
          </h3>
          <p style={{ fontSize: '1.0625rem', color: 'var(--gray-500)' }}>
            Type your question below to get AI-powered answers
          </p>

          {/* Suggested questions */}
          <div style={{ marginTop: '1.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem', justifyContent: 'center' }}>
            {[
              'What is the main topic?',
              'Summarize key findings',
              'What are the conclusions?',
              'List important facts',
            ].map((q) => (
              <span key={q} style={{
                padding: '0.5rem 1rem',
                background: 'var(--white)',
                border: '2px solid var(--black)',
                fontSize: '0.9375rem',
                color: 'var(--black)',
                fontWeight: 600,
                cursor: 'default',
              }}>
                {q}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="chat-messages">
      <AnimatePresence initial={false}>
        {messages.map((msg, i) => (
          <MessageBubble key={msg.id || `msg-${i}`} message={msg} />
        ))}
      </AnimatePresence>

      {/* Loading indicator */}
      {loading && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ display: 'flex', gap: '0.625rem', alignItems: 'flex-start' }}
        >
          <div style={{
            width: 40, height: 40, flexShrink: 0,
            background: 'var(--black)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.875rem', color: 'white', fontWeight: 700,
            fontFamily: 'var(--font-heading)',
          }}>
            OS
          </div>
          <div style={{
            padding: '1rem 1.25rem',
            background: 'var(--white)',
            border: '2px solid var(--black)',
            display: 'flex', gap: '8px', alignItems: 'center',
          }}>
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                style={{
                  width: 8, height: 8,
                  background: 'var(--black)',
                  display: 'block',
                }}
                animate={{ scale: [1, 1.4, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 0.9, delay: i * 0.2 }}
              />
            ))}
          </div>
        </motion.div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
