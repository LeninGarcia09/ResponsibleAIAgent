'use client'

import styles from './Footer.module.css'

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerContent}>
        <div className={styles.footerMain}>
          <p className={styles.copyright}>
            © {new Date().getFullYear()} Microsoft Corporation. All rights reserved.
          </p>
          <span className={styles.divider}>|</span>
          <span className={styles.confidential}>Pilot Program - Internal & Limited External Use</span>
        </div>
        
        <div className={styles.footerLinks}>
          <a href="/docs/transparency" className={styles.footerLink}>
            Transparency Note
          </a>
          <span className={styles.linkDivider}>•</span>
          <a href="/docs/terms" className={styles.footerLink}>
            Terms of Use
          </a>
          <span className={styles.linkDivider}>•</span>
          <a href="/docs/privacy" className={styles.footerLink}>
            Privacy Statement
          </a>
          <span className={styles.linkDivider}>•</span>
          <a href="mailto:lesalgad@microsoft.com?subject=RAI%20Tools%20Navigator%20Feedback" className={styles.footerLink}>
            Send Feedback
          </a>
        </div>

        <div className={styles.footerContact}>
          <span className={styles.contactLabel}>Tool Owner:</span>
          <a href="mailto:lesalgad@microsoft.com" className={styles.contactLink}>
            Lenin Garcia (lesalgad@microsoft.com)
          </a>
        </div>
      </div>
    </footer>
  )
}
