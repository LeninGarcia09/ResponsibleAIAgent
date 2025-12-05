'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, AIReviewSubmission, AdvancedReviewSubmission, SubmissionResponse, Recommendation, isAIRecommendation } from '@/lib/api'
import styles from './submit.module.css'

type ReviewMode = 'basic' | 'advanced'

export default function SubmitPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SubmissionResponse | null>(null)
  const [reviewMode, setReviewMode] = useState<ReviewMode>('basic')
  const [currentSection, setCurrentSection] = useState(0)
  
  // Basic form data
  const [formData, setFormData] = useState<Partial<AIReviewSubmission>>({
    project_name: '',
    project_description: '',
    deployment_stage: 'Development',
  })

  // Advanced form data
  const [advancedData, setAdvancedData] = useState<Partial<AdvancedReviewSubmission>>({
    project_name: '',
    deployment_stage: 'Development',
    // Purpose & Use Case
    intended_purpose: '',
    business_problem: '',
    end_users: '',
    // Data & Inputs
    data_sources: '',
    data_collection_storage: '',
    sensitive_data: '',
    // Model & Technology
    ai_models: '',
    model_type: '',
    environments_connectors: '',
    // Fairness & Bias
    bias_checking: '',
    bias_mitigation: '',
    // Transparency & Explainability
    decision_explainability: '',
    output_documentation: '',
    // Accountability & Governance
    system_ownership: '',
    escalation_paths: '',
    // Security & Privacy
    data_security: '',
    privacy_compliance: '',
    // Impact & Risk
    potential_risks: '',
    risk_monitoring: '',
    // User Interaction
    user_interaction_method: '',
    human_in_loop: '',
  })

  const advancedSections = [
    { title: 'Project Overview', icon: '📋', fields: ['project_name', 'deployment_stage'] },
    { title: 'Purpose & Use Case', icon: '🎯', fields: ['intended_purpose', 'business_problem', 'end_users'] },
    { title: 'Data & Inputs', icon: '💾', fields: ['data_sources', 'data_collection_storage', 'sensitive_data'] },
    { title: 'Model & Technology', icon: '🤖', fields: ['ai_models', 'model_type', 'environments_connectors'] },
    { title: 'Fairness & Bias', icon: '⚖️', fields: ['bias_checking', 'bias_mitigation'] },
    { title: 'Transparency & Explainability', icon: '🔍', fields: ['decision_explainability', 'output_documentation'] },
    { title: 'Accountability & Governance', icon: '👥', fields: ['system_ownership', 'escalation_paths'] },
    { title: 'Security & Privacy', icon: '🔒', fields: ['data_security', 'privacy_compliance'] },
    { title: 'Impact & Risk', icon: '⚠️', fields: ['potential_risks', 'risk_monitoring'] },
    { title: 'User Interaction', icon: '💬', fields: ['user_interaction_method', 'human_in_loop'] }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      if (reviewMode === 'basic') {
        if (!formData.project_name) {
          throw new Error('Please provide a project name')
        }
        const response = await apiClient.submitReview(formData as AIReviewSubmission)
        setResult(response)
      } else {
        if (!advancedData.project_name) {
          throw new Error('Please provide a project name')
        }
        const response = await apiClient.submitAdvancedReview(advancedData as AdvancedReviewSubmission)
        setResult(response)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed')
      console.error('Submission error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getPriorityClass = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical':
        return styles.priorityCritical
      case 'high':
        return styles.priorityHigh
      case 'medium':
        return styles.priorityMedium
      default:
        return styles.priorityLow
    }
  }

  const renderModeSelector = () => (
    <div className={styles.modeSelector}>
      <button
        type="button"
        className={`${styles.modeButton} ${reviewMode === 'basic' ? styles.modeActive : ''}`}
        onClick={() => setReviewMode('basic')}
      >
        <span className={styles.modeIcon}>⚡</span>
        <div className={styles.modeContent}>
          <span className={styles.modeTitle}>Basic Review</span>
          <span className={styles.modeDesc}>Quick assessment with project name and description</span>
        </div>
      </button>
      <button
        type="button"
        className={`${styles.modeButton} ${reviewMode === 'advanced' ? styles.modeActive : ''}`}
        onClick={() => setReviewMode('advanced')}
      >
        <span className={styles.modeIcon}>🔬</span>
        <div className={styles.modeContent}>
          <span className={styles.modeTitle}>Comprehensive Review</span>
          <span className={styles.modeDesc}>In-depth analysis with detailed questionnaire</span>
        </div>
      </button>
    </div>
  )

  const renderBasicForm = () => (
    <section className={styles.section}>
      <h2 className={styles.sectionTitle}>Project Information</h2>
      <p className={styles.sectionDescription}>
        Provide basic details about your AI project for a quick Responsible AI assessment.
      </p>

      <div className={styles.formGroup}>
        <label className={styles.label}>
          Project Name <span className={styles.required}>*</span>
        </label>
        <input
          type="text"
          value={formData.project_name}
          onChange={(e) => setFormData(prev => ({ ...prev, project_name: e.target.value }))}
          className={styles.input}
          required
          placeholder="e.g., Customer Service AI Chatbot"
        />
      </div>

      <div className={styles.formGroup}>
        <label className={styles.label}>
          Project Description / Question
        </label>
        <textarea
          value={formData.project_description}
          onChange={(e) => setFormData(prev => ({ ...prev, project_description: e.target.value }))}
          className={styles.textarea}
          rows={4}
          placeholder="Describe your AI solution, its purpose, and key features. You can also ask specific questions about Responsible AI practices..."
        />
      </div>

      <div className={styles.formGroup}>
        <label className={styles.label}>Deployment Stage</label>
        <select
          value={formData.deployment_stage}
          onChange={(e) => setFormData(prev => ({ ...prev, deployment_stage: e.target.value }))}
          className={styles.select}
        >
          <option value="Planning">Planning</option>
          <option value="Development">Development</option>
          <option value="Testing">Testing</option>
          <option value="Staging">Staging</option>
          <option value="Production">Production</option>
        </select>
      </div>
    </section>
  )

  const renderAdvancedSection = (sectionIndex: number) => {
    const section = advancedSections[sectionIndex]
    
    return (
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionIcon}>{section.icon}</span>
          <div>
            <h2 className={styles.sectionTitle}>{section.title}</h2>
            <p className={styles.sectionDescription}>
              Step {sectionIndex + 1} of {advancedSections.length}
            </p>
          </div>
        </div>

        {sectionIndex === 0 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Project Name <span className={styles.required}>*</span>
              </label>
              <input
                type="text"
                value={advancedData.project_name}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, project_name: e.target.value }))}
                className={styles.input}
                required
                placeholder="e.g., Customer Service AI Chatbot"
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Deployment Stage</label>
              <select
                value={advancedData.deployment_stage}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, deployment_stage: e.target.value }))}
                className={styles.select}
              >
                <option value="Planning">Planning</option>
                <option value="Development">Development</option>
                <option value="Testing">Testing</option>
                <option value="Staging">Staging</option>
                <option value="Production">Production</option>
              </select>
            </div>
          </>
        )}

        {sectionIndex === 1 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>What is the AI system&apos;s intended purpose?</label>
              <textarea
                value={advancedData.intended_purpose}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, intended_purpose: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe the primary function and goals of your AI system..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>What business problem does it solve?</label>
              <textarea
                value={advancedData.business_problem}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, business_problem: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Explain the specific business challenge this AI addresses..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Who are the end users?</label>
              <textarea
                value={advancedData.end_users}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, end_users: e.target.value }))}
                className={styles.textarea}
                rows={2}
                placeholder="Describe the target audience (customers, employees, partners, etc.)..."
              />
            </div>
          </>
        )}

        {sectionIndex === 2 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>What data sources are used?</label>
              <textarea
                value={advancedData.data_sources}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, data_sources: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="List the data sources (databases, APIs, user inputs, third-party data, etc.)..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>How is data collected, stored, and processed?</label>
              <textarea
                value={advancedData.data_collection_storage}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, data_collection_storage: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe data flows, storage locations, processing pipelines..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Are there any sensitive or personal data elements?</label>
              <textarea
                value={advancedData.sensitive_data}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, sensitive_data: e.target.value }))}
                className={styles.textarea}
                rows={2}
                placeholder="Identify PII, PHI, financial data, or other sensitive information..."
              />
            </div>
          </>
        )}

        {sectionIndex === 3 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>What AI models or techniques are being used?</label>
              <textarea
                value={advancedData.ai_models}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, ai_models: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="e.g., GPT-4o, Azure OpenAI, custom ML models, computer vision, etc."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Are these models pre-trained or custom-built?</label>
              <select
                value={advancedData.model_type}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, model_type: e.target.value }))}
                className={styles.select}
              >
                <option value="">Select model type...</option>
                <option value="pre-trained">Pre-trained (e.g., Azure OpenAI, Cognitive Services)</option>
                <option value="fine-tuned">Fine-tuned (pre-trained + custom training)</option>
                <option value="custom">Custom-built (trained from scratch)</option>
                <option value="hybrid">Hybrid (combination of approaches)</option>
              </select>
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>What environments and connectors are involved?</label>
              <textarea
                value={advancedData.environments_connectors}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, environments_connectors: e.target.value }))}
                className={styles.textarea}
                rows={2}
                placeholder="Dev/Test/Prod environments, Azure services, external APIs, integrations..."
              />
            </div>
          </>
        )}

        {sectionIndex === 4 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>How do you check for bias in data and outputs?</label>
              <textarea
                value={advancedData.bias_checking}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, bias_checking: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe bias detection methods, testing procedures, metrics used..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>What mitigation strategies are in place?</label>
              <textarea
                value={advancedData.bias_mitigation}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, bias_mitigation: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe how you address identified biases (retraining, data balancing, etc.)..."
              />
            </div>
          </>
        )}

        {sectionIndex === 5 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>Can the system&apos;s decisions be explained to users?</label>
              <textarea
                value={advancedData.decision_explainability}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, decision_explainability: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe how users understand why the AI made certain decisions..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Are outputs interpretable and documented?</label>
              <textarea
                value={advancedData.output_documentation}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, output_documentation: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe documentation, confidence scores, uncertainty indicators..."
              />
            </div>
          </>
        )}

        {sectionIndex === 6 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>Who owns the system and its outcomes?</label>
              <textarea
                value={advancedData.system_ownership}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, system_ownership: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Identify responsible teams, stakeholders, decision-makers..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>What escalation paths exist for issues?</label>
              <textarea
                value={advancedData.escalation_paths}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, escalation_paths: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe incident response, reporting channels, escalation procedures..."
              />
            </div>
          </>
        )}

        {sectionIndex === 7 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>How is data secured in transit and at rest?</label>
              <textarea
                value={advancedData.data_security}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, data_security: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe encryption, access controls, authentication methods..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Are privacy regulations (GDPR, etc.) addressed?</label>
              <textarea
                value={advancedData.privacy_compliance}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, privacy_compliance: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe compliance measures, data retention policies, user consent..."
              />
            </div>
          </>
        )}

        {sectionIndex === 8 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>What are the potential risks to users or society?</label>
              <textarea
                value={advancedData.potential_risks}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, potential_risks: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Identify possible harms, misuse scenarios, unintended consequences..."
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>How do you monitor and mitigate unintended consequences?</label>
              <textarea
                value={advancedData.risk_monitoring}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, risk_monitoring: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="Describe monitoring systems, feedback loops, incident response..."
              />
            </div>
          </>
        )}

        {sectionIndex === 9 && (
          <>
            <div className={styles.formGroup}>
              <label className={styles.label}>How do users interact with the system?</label>
              <select
                value={advancedData.user_interaction_method}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, user_interaction_method: e.target.value }))}
                className={styles.select}
              >
                <option value="">Select interaction method...</option>
                <option value="chatbot">Chatbot / Conversational AI</option>
                <option value="api">API Integration</option>
                <option value="web-ui">Web Application UI</option>
                <option value="mobile">Mobile Application</option>
                <option value="embedded">Embedded in other applications</option>
                <option value="automated">Fully automated (no direct user interaction)</option>
                <option value="multiple">Multiple interaction methods</option>
              </select>
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Is there a human-in-the-loop for critical decisions?</label>
              <select
                value={advancedData.human_in_loop}
                onChange={(e) => setAdvancedData(prev => ({ ...prev, human_in_loop: e.target.value }))}
                className={styles.select}
              >
                <option value="">Select...</option>
                <option value="always">Yes, always for all decisions</option>
                <option value="critical">Yes, for critical decisions only</option>
                <option value="review">Yes, periodic human review</option>
                <option value="override">No, but human can override</option>
                <option value="no">No human-in-the-loop</option>
              </select>
            </div>
          </>
        )}
      </section>
    )
  }

  const renderProgressBar = () => (
    <div className={styles.progressContainer}>
      <div className={styles.progressBar}>
        {advancedSections.map((section, index) => (
          <button
            key={index}
            type="button"
            className={`${styles.progressStep} ${index === currentSection ? styles.progressActive : ''} ${index < currentSection ? styles.progressComplete : ''}`}
            onClick={() => setCurrentSection(index)}
            title={section.title}
          >
            <span className={styles.progressIcon}>{section.icon}</span>
          </button>
        ))}
      </div>
      <div className={styles.progressLabel}>
        {advancedSections[currentSection].title}
      </div>
    </div>
  )

  const renderAdvancedNavigation = () => (
    <div className={styles.navigationButtons}>
      <button
        type="button"
        onClick={() => setCurrentSection(prev => prev - 1)}
        disabled={currentSection === 0}
        className={styles.navButton}
      >
        ← Previous
      </button>
      <span className={styles.stepIndicator}>
        {currentSection + 1} / {advancedSections.length}
      </span>
      {currentSection < advancedSections.length - 1 ? (
        <button
          type="button"
          onClick={() => setCurrentSection(prev => prev + 1)}
          className={styles.navButton}
        >
          Next →
        </button>
      ) : (
        <button
          type="submit"
          disabled={loading}
          className={styles.submitButton}
        >
          {loading ? 'Analyzing...' : 'Get AI Recommendations'}
        </button>
      )}
    </div>
  )

  const renderRecommendation = (rec: Recommendation, index: number) => {
    if (isAIRecommendation(rec)) {
      return (
        <div key={rec.id || index} className={styles.recommendationCard}>
          <div className={styles.cardHeader}>
            <h3 className={styles.principle}>{rec.principle}</h3>
            <span className={`${styles.priorityBadge} ${getPriorityClass(rec.priority)}`}>
              {rec.priority}
            </span>
          </div>

          <div className={styles.cardBody}>
            <h4 className={styles.recTitle}>{rec.title}</h4>
            
            <div className={styles.issueSection}>
              <strong>Issue:</strong> {rec.issue}
            </div>
            
            <div className={styles.recSection}>
              <strong>Recommendation:</strong> {rec.recommendation}
            </div>

            {rec.implementation_steps && rec.implementation_steps.length > 0 && (
              <>
                <h4 className={styles.subsectionTitle}>Implementation Steps:</h4>
                <ol className={styles.stepsList}>
                  {rec.implementation_steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </>
            )}

            {rec.effort && rec.impact && (
              <div className={styles.effortImpact}>
                <span className={styles.badge}>Effort: {rec.effort}</span>
                <span className={styles.badge}>Impact: {rec.impact}</span>
              </div>
            )}

            {rec.tools && rec.tools.length > 0 && (
              <>
                <h4 className={styles.subsectionTitle}>Recommended Tools:</h4>
                <div className={styles.toolsList}>
                  {rec.tools.map((tool, idx) => (
                    <div key={idx} className={styles.toolCard}>
                      <a
                        href={tool.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.toolName}
                      >
                        {tool.name} ↗
                      </a>
                      <p className={styles.toolDescription}>
                        {tool.purpose || tool.description}
                      </p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )
    } else {
      return (
        <div key={index} className={styles.recommendationCard}>
          <div className={styles.cardHeader}>
            <h3 className={styles.principle}>{rec.principle}</h3>
            <span className={`${styles.priorityBadge} ${getPriorityClass(rec.priority)}`}>
              {rec.priority}
            </span>
          </div>

          <div className={styles.cardBody}>
            {rec.description && (
              <p className={styles.description}>{rec.description}</p>
            )}

            <h4 className={styles.subsectionTitle}>Recommendations:</h4>
            <ul className={styles.recommendationList}>
              {rec.recommendations.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>

            {rec.tools && rec.tools.length > 0 && (
              <>
                <h4 className={styles.subsectionTitle}>Recommended Tools:</h4>
                <div className={styles.toolsList}>
                  {rec.tools.map((tool, idx) => (
                    <div key={idx} className={styles.toolCard}>
                      <a
                        href={tool.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.toolName}
                      >
                        {tool.name} ↗
                      </a>
                      <p className={styles.toolDescription}>{tool.description}</p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <button onClick={() => router.push('/')} className={styles.backButton}>
          ← Back to Home
        </button>
        <h1 className={styles.title}>AI Solution Review</h1>
        <p className={styles.subtitle}>
          Get instant Responsible AI recommendations powered by Azure OpenAI
        </p>
      </header>

      {!result ? (
        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}

          {renderModeSelector()}

          {reviewMode === 'basic' ? (
            <>
              {renderBasicForm()}
              <div className={styles.submitSection}>
                <button
                  type="submit"
                  disabled={loading}
                  className={styles.submitButton}
                >
                  {loading ? 'Analyzing with AI...' : 'Get AI Recommendations'}
                </button>
                <button
                  type="button"
                  onClick={() => router.push('/')}
                  className={styles.cancelButton}
                >
                  Cancel
                </button>
              </div>
            </>
          ) : (
            <>
              {renderProgressBar()}
              {renderAdvancedSection(currentSection)}
              {renderAdvancedNavigation()}
            </>
          )}
        </form>
      ) : (
        <div className={styles.results}>
          <div className={styles.resultHeader}>
            <div className={styles.titleRow}>
              <h2>Recommendations for: {result.project_name}</h2>
              {result.ai_powered && (
                <span className={styles.aiPoweredBadge}>✨ AI-Powered</span>
              )}
            </div>
            
            {result.overall_assessment && (
              <div className={styles.overallAssessment}>
                <p className={styles.assessmentSummary}>{result.overall_assessment.summary}</p>
                <div className={styles.maturityLevel}>
                  <strong>Maturity Level:</strong> {result.overall_assessment.maturity_level}
                </div>
                {result.overall_assessment.key_strengths && result.overall_assessment.key_strengths.length > 0 && (
                  <div className={styles.strengths}>
                    <strong>Key Strengths:</strong>
                    <ul>
                      {result.overall_assessment.key_strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <div className={styles.summary}>
              <span className={styles.summaryItem}>
                Total: <strong>{result.summary.total_recommendations}</strong>
              </span>
              <span className={styles.summaryItem}>
                Critical: <strong className={styles.criticalCount}>{result.summary.critical_items}</strong>
              </span>
              <span className={styles.summaryItem}>
                High: <strong className={styles.highCount}>{result.summary.high_priority_items}</strong>
              </span>
            </div>
            <p className={styles.submissionId}>Submission ID: {result.submission_id}</p>
          </div>

          {result.next_steps && result.next_steps.length > 0 && (
            <div className={styles.nextSteps}>
              <h3>Immediate Next Steps</h3>
              <ol>
                {result.next_steps.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          {/* Quick-Start Guide Section */}
          {result.quick_start_guide && (
            <div className={styles.quickStartGuide}>
              <h3 className={styles.quickStartTitle}>🚀 Quick-Start Guide</h3>
              <p className={styles.quickStartSubtitle}>Actionable steps to begin your Responsible AI journey</p>
              
              {/* Week One Checklist */}
              {result.quick_start_guide.week_one_checklist && result.quick_start_guide.week_one_checklist.length > 0 && (
                <div className={styles.quickStartSection}>
                  <h4>📋 Week One Checklist</h4>
                  <div className={styles.checklistGrid}>
                    {result.quick_start_guide.week_one_checklist.map((item, i) => (
                      <div key={i} className={`${styles.checklistItem} ${styles[`priority${item.priority}`]}`}>
                        <span className={styles.checklistTask}>{item.task}</span>
                        {item.resource_url && (
                          <a href={item.resource_url} target="_blank" rel="noopener noreferrer" className={styles.checklistLink}>
                            View Resource ↗
                          </a>
                        )}
                        <span className={styles.checklistPriority}>{item.priority}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Essential Tools */}
              {result.quick_start_guide.essential_tools && result.quick_start_guide.essential_tools.length > 0 && (
                <div className={styles.quickStartSection}>
                  <h4>🛠️ Essential Tools to Install First</h4>
                  <div className={styles.essentialToolsGrid}>
                    {result.quick_start_guide.essential_tools.map((tool, i) => (
                      <div key={i} className={styles.essentialToolCard}>
                        <a href={tool.url} target="_blank" rel="noopener noreferrer" className={styles.essentialToolName}>
                          {tool.name} ↗
                        </a>
                        <p className={styles.essentialToolPurpose}>{tool.purpose}</p>
                        {tool.install_command && (
                          <code className={styles.installCommand}>{tool.install_command}</code>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 30-Day Roadmap */}
              {result.quick_start_guide.thirty_day_roadmap && (
                <div className={styles.quickStartSection}>
                  <h4>📅 30-Day Roadmap</h4>
                  <div className={styles.roadmapGrid}>
                    {Object.entries(result.quick_start_guide.thirty_day_roadmap).map(([week, data]) => (
                      data && (
                        <div key={week} className={styles.roadmapWeek}>
                          <h5 className={styles.weekTitle}>{week.replace('_', ' ').toUpperCase()}</h5>
                          <span className={styles.weekFocus}>{data.focus}</span>
                          <ul className={styles.weekActions}>
                            {data.actions.map((action, i) => (
                              <li key={i}>{action}</li>
                            ))}
                          </ul>
                        </div>
                      )
                    ))}
                  </div>
                </div>
              )}

              {/* Quick Reference */}
              {result.quick_start_guide.quick_reference && (
                <div className={styles.quickStartSection}>
                  <h4>⚡ Quick Reference Card</h4>
                  <div className={styles.quickReferenceGrid}>
                    <div className={styles.referenceCard}>
                      <h5>🔧 Top Tools</h5>
                      <ul>
                        {result.quick_start_guide.quick_reference.top_3_tools.map((tool, i) => (
                          <li key={i}>{tool}</li>
                        ))}
                      </ul>
                    </div>
                    <div className={styles.referenceCard}>
                      <h5>📊 Key Metrics</h5>
                      <ul>
                        {result.quick_start_guide.quick_reference.key_metrics.map((metric, i) => (
                          <li key={i}>{metric}</li>
                        ))}
                      </ul>
                    </div>
                    <div className={styles.referenceCard}>
                      <h5>🚨 Red Flags</h5>
                      <ul className={styles.redFlagsList}>
                        {result.quick_start_guide.quick_reference.red_flags.map((flag, i) => (
                          <li key={i}>{flag}</li>
                        ))}
                      </ul>
                    </div>
                    <div className={styles.referenceCard}>
                      <h5>👥 Stakeholders</h5>
                      <ul>
                        {result.quick_start_guide.quick_reference.stakeholders_to_involve.map((role, i) => (
                          <li key={i}>{role}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* Templates & Checklists */}
              {result.quick_start_guide.templates_and_checklists && result.quick_start_guide.templates_and_checklists.length > 0 && (
                <div className={styles.quickStartSection}>
                  <h4>📝 Templates & Checklists</h4>
                  <div className={styles.templatesGrid}>
                    {result.quick_start_guide.templates_and_checklists.map((template, i) => (
                      <a key={i} href={template.url} target="_blank" rel="noopener noreferrer" className={styles.templateCard}>
                        <span className={styles.templateName}>{template.name}</span>
                        <span className={styles.templatePurpose}>{template.purpose}</span>
                        <span className={styles.templateLink}>Open Template ↗</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Reference Links Section */}
          {result.reference_links && (
            <div className={styles.referenceLinks}>
              <h3>📚 Reference Links</h3>
              <div className={styles.referenceSections}>
                {result.reference_links.getting_started && result.reference_links.getting_started.length > 0 && (
                  <div className={styles.referenceSection}>
                    <h4>Getting Started</h4>
                    {result.reference_links.getting_started.map((link, i) => (
                      <a key={i} href={link.url} target="_blank" rel="noopener noreferrer" className={styles.referenceItem}>
                        <span className={styles.refTitle}>{link.title}</span>
                        <span className={styles.refDesc}>{link.description}</span>
                      </a>
                    ))}
                  </div>
                )}
                {result.reference_links.tools_documentation && result.reference_links.tools_documentation.length > 0 && (
                  <div className={styles.referenceSection}>
                    <h4>Tools Documentation</h4>
                    {result.reference_links.tools_documentation.map((link, i) => (
                      <a key={i} href={link.url} target="_blank" rel="noopener noreferrer" className={styles.referenceItem}>
                        <span className={styles.refTitle}>{link.title}</span>
                        <span className={styles.refDesc}>{link.description}</span>
                      </a>
                    ))}
                  </div>
                )}
                {result.reference_links.templates && result.reference_links.templates.length > 0 && (
                  <div className={styles.referenceSection}>
                    <h4>Templates</h4>
                    {result.reference_links.templates.map((link, i) => (
                      <a key={i} href={link.url} target="_blank" rel="noopener noreferrer" className={styles.referenceItem}>
                        <span className={styles.refTitle}>{link.title}</span>
                        <span className={styles.refDesc}>{link.description}</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          <div className={styles.recommendations}>
            {result.recommendations.map((rec, index) => renderRecommendation(rec, index))}
          </div>

          <div className={styles.actionButtons}>
            <button
              onClick={() => {
                setResult(null)
                setFormData({ project_name: '', project_description: '', deployment_stage: 'Development' })
                setAdvancedData({
                  project_name: '',
                  deployment_stage: 'Development',
                  intended_purpose: '',
                  business_problem: '',
                  end_users: '',
                  data_sources: '',
                  data_collection_storage: '',
                  sensitive_data: '',
                  ai_models: '',
                  model_type: '',
                  environments_connectors: '',
                  bias_checking: '',
                  bias_mitigation: '',
                  decision_explainability: '',
                  output_documentation: '',
                  system_ownership: '',
                  escalation_paths: '',
                  data_security: '',
                  privacy_compliance: '',
                  potential_risks: '',
                  risk_monitoring: '',
                  user_interaction_method: '',
                  human_in_loop: '',
                })
                setCurrentSection(0)
              }}
              className={styles.submitButton}
            >
              Review Another Project
            </button>
            <button
              onClick={() => router.push('/')}
              className={styles.cancelButton}
            >
              Back to Home
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
