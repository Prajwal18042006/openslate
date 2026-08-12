export default function DetailInspector({ title = 'Detail Inspector', content }) {
  if (!content) {
    return (
      <aside className="detail-inspector">
        <div className="detail-inspector-header">{title}</div>
        <div className="detail-inspector-body">
          <p style={{ color: 'var(--gray-400)', fontSize: '1rem' }}>
            Select a chunk or pipeline stage to inspect details here.
          </p>
        </div>
      </aside>
    )
  }

  return (
    <aside className="detail-inspector">
      <div className="detail-inspector-header">{title}</div>
      <div className="detail-inspector-body">
        <h4 className="detail-inspector-title">{content.title}</h4>

        {content.meta?.length > 0 && (
          <div className="detail-meta">
            {content.meta.map((tag) => (
              <span key={tag} className="detail-meta-tag">{tag}</span>
            ))}
          </div>
        )}

        {content.stats?.length > 0 && (
          <div style={{ marginBottom: '1.25rem' }}>
            {content.stats.map((stat) => (
              <div key={stat} style={{
                fontSize: '0.9375rem', padding: '0.5rem 0',
                borderBottom: '1px solid var(--gray-100)', color: 'var(--gray-600)',
              }}>
                {stat}
              </div>
            ))}
          </div>
        )}

        <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {content.body}
        </div>
      </div>
    </aside>
  )
}
