'use client'

import { useState } from 'react'
import styles from './FeedbackButton.module.css'

interface FeedbackButtonProps {
  context?: string
}

export default function FeedbackButton({ context }: FeedbackButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [feedbackType, setFeedbackType] = useState<'positive' | 'negative' | 'suggestion' | null>(null)
  const [feedbackText, setFeedbackText] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async () => {
    if (!feedbackType) return
    
    setIsSubmitting(true)
    
    // Create mailto link with feedback
    const subject = `RAI Tools Navigator Feedback - ${feedbackType.charAt(0).toUpperCase() + feedbackType.slice(1)}`
    const body = `
Feedback Type: ${feedbackType}
Context: ${context || 'General'}
Date: ${new Date().toISOString()}

Feedback:
${feedbackText || 'No additional comments'}

---
Sent from RAI Tools Navigator Feedback Widget
    `.trim()
    
    // Open email client
    window.location.href = `mailto:lesalgad@microsoft.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
    
    setIsSubmitting(false)
    setSubmitted(true)
    
    // Reset after delay
    setTimeout(() => {
      setIsOpen(false)
      setSubmitted(false)
      setFeedbackType(null)
      setFeedbackText('')
    }, 2000)
  }

  if (!isOpen) {
    return (
      <button 
        className={styles.feedbackTrigger}
        onClick={() => setIsOpen(true)}
        aria-label="Send feedback"
      >
        💬 Feedback
      </button>
    )
  }

  return (
    <div className={styles.feedbackPanel}>
      <div className={styles.feedbackHeader}>
        <h3>Send Feedback</h3>
        <button 
          className={styles.closeBtn}
          onClick={() => setIsOpen(false)}
          aria-label="Close feedback"
        >
          ✕
        </button>
      </div>

      {submitted ? (
        <div className={styles.successMessage}>
          <span className={styles.successIcon}>✓</span>
          <p>Thank you for your feedback!</p>
        </div>
      ) : (
        <>
          <div className={styles.feedbackTypes}>
            <p className={styles.typeLabel}>How was your experience?</p>
            <div className={styles.typeButtons}>
              <button
                className={`${styles.typeBtn} ${feedbackType === 'positive' ? styles.selected : ''}`}
                onClick={() => setFeedbackType('positive')}
              >
                👍 Good
              </button>
              <button
                className={`${styles.typeBtn} ${feedbackType === 'negative' ? styles.selected : ''}`}
                onClick={() => setFeedbackType('negative')}
              >
                👎 Needs Work
              </button>
              <button
                className={`${styles.typeBtn} ${feedbackType === 'suggestion' ? styles.selected : ''}`}
                onClick={() => setFeedbackType('suggestion')}
              >
                💡 Suggestion
              </button>
            </div>
          </div>

          <div className={styles.feedbackInput}>
            <label htmlFor="feedback-text">Tell us more (optional):</label>
            <textarea
              id="feedback-text"
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="What did you like? What could be better?"
              rows={3}
            />
          </div>

          <button
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={!feedbackType || isSubmitting}
          >
            {isSubmitting ? 'Opening Email...' : 'Send Feedback'}
          </button>

          <p className={styles.privacyNote}>
            Feedback is sent to the tool owner via email.
          </p>
        </>
      )}
    </div>
  )
}
