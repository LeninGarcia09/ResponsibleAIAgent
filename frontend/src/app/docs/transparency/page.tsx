import Link from 'next/link'
import styles from '../docs.module.css'
import Footer from '../../../components/Footer'

export default function TransparencyNotePage() {
  return (
    <div className={styles.container}>
      <div className={styles.pilotBanner}>
        <span>⚠️</span>
        <span>
          <strong>PILOT ONLY</strong> — This is a pilot program. For questions, contact: <a href="mailto:lesalgad@microsoft.com">Lenin Garcia</a>
        </span>
      </div>

      <header className={styles.header}>
        <div className={styles.headerContent}>
          <Link href="/" className={styles.backLink}>
            ← Back to Home
          </Link>
          <h1 className={styles.title}>📋 Transparency Note</h1>
          <p className={styles.lastUpdated}>Last Updated: January 2025 | Version 1.0.0</p>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.content}>
          <h2>1. What is the RAI Tools Navigator?</h2>
          <p>
            The RAI Tools Navigator is an AI-powered conversational assistant designed to help users discover, 
            understand, and select appropriate Microsoft Responsible AI (RAI) tools and frameworks for their AI projects.
          </p>
          
          <h3>System Components</h3>
          <ul>
            <li><strong>Conversational AI Interface:</strong> Powered by Azure OpenAI GPT-4o</li>
            <li><strong>Knowledge Base:</strong> Curated catalog of Microsoft RAI tools and frameworks</li>
            <li><strong>RAG System:</strong> Retrieval-Augmented Generation for contextual responses</li>
            <li><strong>Tools Catalog:</strong> Searchable database of RAI tools organized by category</li>
          </ul>

          <h2>2. What can the system do?</h2>
          <ul>
            <li>Answer questions about Microsoft's Responsible AI tools</li>
            <li>Recommend appropriate tools based on described scenarios</li>
            <li>Explain tool capabilities, prerequisites, and limitations</li>
            <li>Compare tools across RAI pillars (Fairness, Reliability, Privacy, etc.)</li>
            <li>Provide guidance on implementation considerations</li>
          </ul>

          <h2>3. What are the system's limitations?</h2>
          
          <h3>Content Accuracy</h3>
          <ul>
            <li>Responses are AI-generated and may contain errors or omissions</li>
            <li>Information is based on a curated knowledge base, not real-time documentation</li>
            <li>The system may occasionally produce plausible but incorrect information</li>
          </ul>

          <h3>Scope Limitations</h3>
          <ul>
            <li>Limited to tools in the curated catalog</li>
            <li>Cannot access or analyze your specific codebase</li>
            <li>Does not provide medical, legal, or financial advice</li>
            <li>English language only</li>
          </ul>

          <h3>AI Limitations</h3>
          <ul>
            <li>May not understand highly technical or ambiguous queries</li>
            <li>Cannot learn from individual user sessions</li>
            <li>May produce inconsistent responses to similar queries</li>
          </ul>

          <h2>4. How should outputs be interpreted?</h2>
          <p>
            All outputs from this system are <strong>informational guidance only</strong>. They should:
          </p>
          <ul>
            <li>Be verified against official Microsoft documentation</li>
            <li>Be reviewed by qualified personnel before implementation</li>
            <li>Not replace professional judgment or official compliance guidance</li>
            <li>Be considered as starting points for further research</li>
          </ul>

          <h2>5. What data does the system use?</h2>
          <ul>
            <li>User queries are processed to generate responses</li>
            <li>Conversations are not persistently stored</li>
            <li>No personal data is required to use the system</li>
            <li>Usage logs may be retained for debugging and improvement</li>
          </ul>

          <h2>6. Responsible AI Commitment</h2>
          <p>
            This tool is built following Microsoft's Responsible AI principles:
          </p>
          <ul>
            <li><strong>Fairness:</strong> Designed to provide consistent recommendations</li>
            <li><strong>Reliability:</strong> Built on enterprise-grade Azure infrastructure</li>
            <li><strong>Privacy:</strong> Minimizes data collection, no personal data required</li>
            <li><strong>Inclusiveness:</strong> Accessible web interface</li>
            <li><strong>Transparency:</strong> This document and related documentation</li>
            <li><strong>Accountability:</strong> Clear owner contact for feedback</li>
          </ul>

          <div className={styles.contactBox}>
            <h3>📧 Contact Information</h3>
            <p><strong>Tool Owner:</strong> Lenin Garcia</p>
            <p><strong>Email:</strong> <a href="mailto:lesalgad@microsoft.com">lesalgad@microsoft.com</a></p>
          </div>

          <div className={styles.relatedDocs}>
            <h3>Related Documentation</h3>
            <div className={styles.docLinks}>
              <Link href="/docs/terms" className={styles.docLink}>Terms of Use</Link>
              <Link href="/docs/privacy" className={styles.docLink}>Privacy Statement</Link>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
