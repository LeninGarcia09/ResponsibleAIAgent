import Link from 'next/link'
import styles from '../docs.module.css'
import Footer from '../../../components/Footer'

export default function PrivacyStatementPage() {
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
          <h1 className={styles.title}>🔒 Privacy Statement</h1>
          <p className={styles.lastUpdated}>Effective Date: January 2025 | Version 1.0.0</p>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.content}>
          <h2>1. Overview</h2>
          <p>
            This Privacy Statement describes how the RAI Tools Navigator ("the Tool") collects, uses, 
            and protects your information during the pilot phase.
          </p>

          <h2>2. Information We Collect</h2>
          
          <h3>Conversation Data</h3>
          <table>
            <thead>
              <tr>
                <th>Data Type</th>
                <th>Description</th>
                <th>Retention</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>User Queries</td>
                <td>Questions and prompts you enter</td>
                <td>Session + logs</td>
              </tr>
              <tr>
                <td>AI Responses</td>
                <td>The Tool's generated responses</td>
                <td>Session + logs</td>
              </tr>
              <tr>
                <td>Session Context</td>
                <td>Conversation history within a session</td>
                <td>Session duration</td>
              </tr>
            </tbody>
          </table>

          <h3>Data We Do NOT Collect</h3>
          <ul>
            <li>Personal identification information (unless voluntarily provided)</li>
            <li>Authentication credentials (managed by Azure infrastructure)</li>
            <li>Payment information</li>
            <li>Location data</li>
            <li>Device identifiers</li>
          </ul>

          <h2>3. How We Use Your Information</h2>
          <ul>
            <li><strong>Provide Service:</strong> Process your queries and generate responses</li>
            <li><strong>Improve Quality:</strong> Analyze usage to enhance accuracy</li>
            <li><strong>Debug Issues:</strong> Identify and fix technical problems</li>
            <li><strong>Ensure Safety:</strong> Monitor for misuse</li>
          </ul>

          <h2>4. AI Processing</h2>
          <p>
            Your queries are processed by Azure OpenAI Service (GPT-4o) with our RAG system. 
            Microsoft's data handling policies for Azure OpenAI apply.
          </p>

          <h2>5. Data Storage and Security</h2>
          <ul>
            <li>All data transmission encrypted via HTTPS/TLS</li>
            <li>Azure Managed Identity for service authentication</li>
            <li>Data processed in Azure West US 3 region</li>
            <li>No persistent storage of conversation content</li>
          </ul>

          <h3>Data Retention</h3>
          <table>
            <thead>
              <tr>
                <th>Data Type</th>
                <th>Retention Period</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Session Data</td>
                <td>Duration of session</td>
              </tr>
              <tr>
                <td>Application Logs</td>
                <td>30 days</td>
              </tr>
              <tr>
                <td>Error Logs</td>
                <td>90 days</td>
              </tr>
            </tbody>
          </table>

          <h2>6. Data Sharing</h2>
          <p>We share data only with:</p>
          <ul>
            <li><strong>Azure OpenAI:</strong> For AI processing</li>
            <li><strong>Azure Platform:</strong> For infrastructure</li>
          </ul>
          <p>We do NOT share data with third-party advertisers, data brokers, or external analytics services.</p>

          <h2>7. Your Rights</h2>
          <p>During the pilot phase, you may:</p>
          <ul>
            <li>Request information about data collected from your sessions</li>
            <li>Request deletion of your session data</li>
            <li>Opt out of the pilot program at any time</li>
          </ul>
          <p>
            For privacy-related requests, contact <a href="mailto:lesalgad@microsoft.com">lesalgad@microsoft.com</a> 
            with subject line "RAI Tools Navigator - Privacy Request".
          </p>

          <h2>8. Cookies and Tracking</h2>
          <p>The pilot version:</p>
          <ul>
            <li>Does NOT use tracking cookies</li>
            <li>Does NOT use third-party analytics</li>
            <li>Does NOT use advertising trackers</li>
          </ul>

          <h2>9. Children's Privacy</h2>
          <p>
            The Tool is not intended for use by individuals under 18 years of age. We do not 
            knowingly collect information from children.
          </p>

          <h2>10. Microsoft Privacy Practices</h2>
          <p>
            This Tool operates within Microsoft's broader privacy framework. For more information:
          </p>
          <ul>
            <li><a href="https://privacy.microsoft.com/privacystatement" target="_blank" rel="noopener noreferrer">Microsoft Privacy Statement</a></li>
            <li><a href="https://azure.microsoft.com/privacy" target="_blank" rel="noopener noreferrer">Azure Privacy</a></li>
            <li><a href="https://learn.microsoft.com/azure/ai-services/openai/concepts/data-privacy" target="_blank" rel="noopener noreferrer">Azure OpenAI Data Privacy</a></li>
          </ul>

          <div className={styles.contactBox}>
            <h3>📧 Contact Information</h3>
            <p><strong>Privacy Contact:</strong> Lenin Garcia</p>
            <p><strong>Email:</strong> <a href="mailto:lesalgad@microsoft.com">lesalgad@microsoft.com</a></p>
          </div>

          <div className={styles.relatedDocs}>
            <h3>Related Documentation</h3>
            <div className={styles.docLinks}>
              <Link href="/docs/transparency" className={styles.docLink}>Transparency Note</Link>
              <Link href="/docs/terms" className={styles.docLink}>Terms of Use</Link>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
