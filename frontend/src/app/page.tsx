'use client'

import { useRouter } from 'next/navigation'
import styles from './page.module.css'

export default function Home() {
  const router = useRouter()

  return (
    <div className={styles.container}>
      <div className={styles.pilotBanner}>
        <span className={styles.pilotIcon}>⚠️</span>
        <span>
          <strong>PILOT ONLY</strong> — This is a pilot program. Please do not use this as official guidance for Responsible AI. 
          For questions, contact: <a href="mailto:lesalgad@microsoft.com">Lenin Garcia (lesalgad@microsoft.com)</a>
        </span>
      </div>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>🤖 Responsible AI Agent</h1>
          <p className={styles.subtitle}>
            Review AI Solutions Against Microsoft Standards
          </p>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.hero}>
          <h2 className={styles.heroTitle}>
            Welcome to the Responsible AI Review Platform
          </h2>
          <p className={styles.heroDescription}>
            Submit your AI solutions for comprehensive review against Microsoft's Responsible AI 
            Standards and security best practices.
          </p>

          <div className={styles.heroButtons}>
            <button 
              className={styles.btnPrimary} 
              onClick={() => router.push('/submit')}
            >
              Submit for Review
            </button>
            <button 
              className={styles.btnSecondary} 
              onClick={() => router.push('/reviews')}
            >
              View My Reviews
            </button>
            <button 
              className={styles.btnOutline} 
              onClick={() => router.push('/catalog')}
            >
              📚 RAI Tools Catalog
            </button>
          </div>
        </div>

        <div className={styles.features}>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>✅</div>
            <h3 className={styles.featureTitle}>
              Responsible AI Principles
            </h3>
            <p>
              Automated review against fairness, transparency, accountability, privacy, 
              reliability, and inclusiveness standards.
            </p>
          </div>

          <div className={styles.feature}>
            <div className={styles.featureIcon}>🔒</div>
            <h3 className={styles.featureTitle}>
              Security Best Practices
            </h3>
            <p>
              Validation of data encryption, access control, compliance certifications, 
              and secure deployment practices.
            </p>
          </div>

          <div className={styles.feature}>
            <div className={styles.featureIcon}>📊</div>
            <h3 className={styles.featureTitle}>
              Comprehensive Reports
            </h3>
            <p>
              Detailed HTML and PDF reports with findings, recommendations, and compliance 
              scores delivered via email.
            </p>
          </div>

          <div className={styles.feature}>
            <div className={styles.featureIcon}>⚡</div>
            <h3 className={styles.featureTitle}>
              Fast Turnaround
            </h3>
            <p>
              AI-powered automated review process provides results in minutes, 
              not days or weeks.
            </p>
          </div>
        </div>

        <div className={styles.cta}>
          <h2 className={styles.ctaTitle}>
            Ready to get started?
          </h2>
          <p className={styles.ctaDescription}>
            Submit your AI solution for review and receive comprehensive feedback 
            on responsible AI compliance and security.
          </p>
          <button 
            className={styles.btnPrimary} 
            onClick={() => router.push('/submit')}
          >
            Get Started →
          </button>
        </div>
      </main>

      <footer className={styles.footer}>
        <p>
          © {new Date().getFullYear()} Microsoft Corporation. All rights reserved. | 
          Confidential - Internal Use Only
        </p>
      </footer>
    </div>
  )
}
