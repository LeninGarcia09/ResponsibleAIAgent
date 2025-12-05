'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import styles from './reviews.module.css'

interface Review {
  id: string
  project_name: string
  submission_date: string
  status: string
  overall_score?: number
  overall_status?: string
  submitter_name: string
}

export default function ReviewsPage() {
  const router = useRouter()
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  // Mock data for demonstration - replace with actual API call
  useEffect(() => {
    const fetchReviews = async () => {
      try {
        // TODO: Replace with actual API call when backend endpoint is ready
        // const data = await apiClient.listSubmissions(userEmail)
        
        // Mock data
        const mockReviews: Review[] = [
          {
            id: '1',
            project_name: 'Customer Service AI Chatbot',
            submission_date: '2025-12-01T10:30:00Z',
            status: 'completed',
            overall_score: 85,
            overall_status: 'Approved',
            submitter_name: 'John Doe',
          },
          {
            id: '2',
            project_name: 'Predictive Analytics Dashboard',
            submission_date: '2025-12-01T14:20:00Z',
            status: 'in_progress',
            submitter_name: 'Jane Smith',
          },
          {
            id: '3',
            project_name: 'Image Recognition System',
            submission_date: '2025-11-30T09:15:00Z',
            status: 'completed',
            overall_score: 72,
            overall_status: 'Approved with Conditions',
            submitter_name: 'Bob Johnson',
          },
          {
            id: '4',
            project_name: 'Natural Language Processor',
            submission_date: '2025-11-29T16:45:00Z',
            status: 'pending',
            submitter_name: 'Alice Williams',
          },
        ]
        
        setReviews(mockReviews)
      } catch (error) {
        console.error('Failed to fetch reviews:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchReviews()
  }, [])

  const filteredReviews = reviews.filter(review => {
    if (filter === 'all') return true
    return review.status === filter
  })

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'completed':
        return styles.statusCompleted
      case 'in_progress':
        return styles.statusInProgress
      case 'pending':
        return styles.statusPending
      case 'failed':
        return styles.statusFailed
      default:
        return styles.statusPending
    }
  }

  const getScoreClass = (score: number) => {
    if (score >= 80) return styles.scoreGood
    if (score >= 60) return styles.scoreWarning
    return styles.scoreBad
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <button onClick={() => router.push('/')} className={styles.backButton}>
          ← Back to Home
        </button>
        <h1 className={styles.title}>My Reviews</h1>
        <p className={styles.subtitle}>
          View and manage your AI solution review submissions
        </p>
      </header>

      <main className={styles.main}>
        <div className={styles.controls}>
          <div className={styles.filters}>
            <button
              className={`${styles.filterButton} ${filter === 'all' ? styles.active : ''}`}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button
              className={`${styles.filterButton} ${filter === 'pending' ? styles.active : ''}`}
              onClick={() => setFilter('pending')}
            >
              Pending
            </button>
            <button
              className={`${styles.filterButton} ${filter === 'in_progress' ? styles.active : ''}`}
              onClick={() => setFilter('in_progress')}
            >
              In Progress
            </button>
            <button
              className={`${styles.filterButton} ${filter === 'completed' ? styles.active : ''}`}
              onClick={() => setFilter('completed')}
            >
              Completed
            </button>
          </div>

          <button
            className={styles.newButton}
            onClick={() => router.push('/submit')}
          >
            + New Submission
          </button>
        </div>

        {loading ? (
          <div className={styles.loading}>
            <div className={styles.spinner}></div>
            <p>Loading reviews...</p>
          </div>
        ) : filteredReviews.length === 0 ? (
          <div className={styles.empty}>
            <div className={styles.emptyIcon}>📋</div>
            <h2>No reviews found</h2>
            <p>
              {filter === 'all'
                ? "You haven't submitted any AI solutions for review yet."
                : `No ${filter.replace('_', ' ')} reviews found.`}
            </p>
            <button
              className={styles.emptyButton}
              onClick={() => router.push('/submit')}
            >
              Submit Your First Review
            </button>
          </div>
        ) : (
          <div className={styles.reviewsList}>
            {filteredReviews.map(review => (
              <div key={review.id} className={styles.reviewCard}>
                <div className={styles.reviewHeader}>
                  <div>
                    <h3 className={styles.projectName}>{review.project_name}</h3>
                    <p className={styles.submitter}>by {review.submitter_name}</p>
                  </div>
                  <span className={`${styles.statusBadge} ${getStatusBadgeClass(review.status)}`}>
                    {review.status.replace('_', ' ')}
                  </span>
                </div>

                <div className={styles.reviewBody}>
                  <div className={styles.reviewInfo}>
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>Submitted:</span>
                      <span className={styles.infoValue}>{formatDate(review.submission_date)}</span>
                    </div>
                    
                    {review.overall_score !== undefined && (
                      <div className={styles.infoItem}>
                        <span className={styles.infoLabel}>Score:</span>
                        <span className={`${styles.infoValue} ${getScoreClass(review.overall_score)}`}>
                          {review.overall_score}/100
                        </span>
                      </div>
                    )}

                    {review.overall_status && (
                      <div className={styles.infoItem}>
                        <span className={styles.infoLabel}>Result:</span>
                        <span className={styles.infoValue}>{review.overall_status}</span>
                      </div>
                    )}
                  </div>

                  <div className={styles.actions}>
                    {review.status === 'completed' && (
                      <>
                        <button className={styles.actionButton}>
                          📄 View Report
                        </button>
                        <button className={styles.actionButton}>
                          📥 Download PDF
                        </button>
                      </>
                    )}
                    {review.status === 'in_progress' && (
                      <button className={styles.actionButton}>
                        🔄 Check Status
                      </button>
                    )}
                    {review.status === 'pending' && (
                      <button className={styles.actionButton}>
                        ▶️ Start Review
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
