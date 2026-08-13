const LINKEDIN_URL = 'https://www.linkedin.com/in/prajwal-jagtap-2013a62b4'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container site-footer-inner">
        <div className="site-footer-brand">
          <span className="site-footer-dot" aria-hidden="true" />
          <span className="site-footer-name">OpenSlate</span>
          <span className="site-footer-tagline">Document Intelligence</span>
        </div>

        <div className="site-footer-links">
          <a
            href={LINKEDIN_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="site-footer-link"
          >
            LinkedIn
            <span className="site-footer-link-arrow" aria-hidden="true">↗</span>
          </a>
          <span className="site-footer-copy">© {new Date().getFullYear()} Prajwal Jagtap</span>
        </div>
      </div>
    </footer>
  )
}
