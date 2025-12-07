'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, AIReviewSubmission, AdvancedReviewSubmission, SubmissionResponse, Recommendation, isAIRecommendation } from '@/lib/api'
import styles from './submit.module.css'

type ReviewMode = 'basic' | 'advanced'

// Field validation states for accessibility
interface FieldError {
  field: string
  message: string
}

// Live region announcement types
type AnnouncementType = 'polite' | 'assertive'

// Industry options for domain-specific guidance
const INDUSTRY_OPTIONS = [
  { value: '', label: 'Select an industry...' },
  { value: 'healthcare', label: '🏥 Healthcare & Life Sciences' },
  { value: 'finance', label: '💰 Financial Services & Banking' },
  { value: 'hr', label: '👥 Human Resources & Recruitment' },
  { value: 'customer_service', label: '💬 Customer Service & Support' },
  { value: 'education', label: '📚 Education & E-Learning' },
  { value: 'government', label: '🏛️ Government & Public Sector' },
  { value: 'retail', label: '🛒 Retail & E-Commerce' },
  { value: 'manufacturing', label: '🏭 Manufacturing & Industrial' },
  { value: 'legal', label: '⚖️ Legal & Compliance' },
  { value: 'media', label: '📺 Media & Entertainment' },
  { value: 'other', label: '🔷 Other' },
]

// Use case types for reference architecture matching
const USE_CASE_OPTIONS = [
  { value: '', label: 'Select use case type...' },
  { value: 'chatbot', label: '💬 Chatbot / Virtual Assistant' },
  { value: 'content_generation', label: '✍️ Content Generation' },
  { value: 'document_processing', label: '📄 Document Processing & Analysis' },
  { value: 'recommendation', label: '🎯 Recommendation System' },
  { value: 'image_analysis', label: '🖼️ Image / Video Analysis' },
  { value: 'predictive_analytics', label: '📊 Predictive Analytics' },
  { value: 'automation', label: '⚙️ Process Automation' },
  { value: 'search', label: '🔍 Intelligent Search (RAG)' },
  { value: 'code_assistant', label: '💻 Code Assistant / Developer Tools' },
  { value: 'decision_support', label: '🧠 Decision Support System' },
  { value: 'other', label: '🔷 Other' },
]

// AI capabilities that may trigger specific risk assessments
const AI_CAPABILITIES = [
  { id: 'personal_data', label: 'Processes personal/PII data', risk: 'high' },
  { id: 'decisions', label: 'Makes or influences decisions about people', risk: 'high' },
  { id: 'content_gen', label: 'Generates content (text, images, code)', risk: 'medium' },
  { id: 'facial_recognition', label: 'Uses facial recognition or biometrics', risk: 'critical' },
  { id: 'autonomous', label: 'Operates autonomously without human oversight', risk: 'high' },
  { id: 'financial', label: 'Handles financial transactions or advice', risk: 'high' },
  { id: 'health_data', label: 'Processes health or medical data', risk: 'critical' },
  { id: 'children', label: 'Designed for or accessible by children', risk: 'high' },
  { id: 'public_facing', label: 'Public-facing / customer-facing', risk: 'medium' },
  { id: 'employee_monitoring', label: 'Monitors employee behavior or performance', risk: 'high' },
]

// Data sensitivity levels
const DATA_SENSITIVITY_OPTIONS = [
  { value: '', label: 'Select data sensitivity...' },
  { value: 'public', label: '🟢 Public data only' },
  { value: 'internal', label: '🟡 Internal/business data' },
  { value: 'confidential', label: '🟠 Confidential data' },
  { value: 'pii', label: '🔴 Personal Identifiable Information (PII)' },
  { value: 'sensitive_pii', label: '🔴 Sensitive PII (health, financial, biometric)' },
  { value: 'regulated', label: '⚫ Regulated data (HIPAA, GDPR, etc.)' },
]

export default function SubmitPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SubmissionResponse | null>(null)
  const [reviewMode, setReviewMode] = useState<ReviewMode>('basic')
  const [currentSection, setCurrentSection] = useState(0)
  
  // Accessibility: Field-level validation errors
  const [fieldErrors, setFieldErrors] = useState<FieldError[]>([])
  
  // Accessibility: Refs for focus management
  const formRef = useRef<HTMLFormElement>(null)
  const errorRef = useRef<HTMLDivElement>(null)
  const sectionRef = useRef<HTMLElement>(null)
  const announcerRef = useRef<HTMLDivElement>(null)
  
  // Accessibility: Live region announcements for screen readers
  const announce = useCallback((message: string, type: AnnouncementType = 'polite') => {
    if (announcerRef.current) {
      announcerRef.current.setAttribute('aria-live', type)
      announcerRef.current.textContent = message
      // Clear after announcement
      setTimeout(() => {
        if (announcerRef.current) announcerRef.current.textContent = ''
      }, 1000)
    }
  }, [])
  
  // Basic form data with enhanced inputs
  const [formData, setFormData] = useState<Partial<AIReviewSubmission>>({
    project_name: '',
    project_description: '',
    deployment_stage: 'Development',
    industry: '',
    technology_type: '',
    target_users: '',
    data_types: '',
    ai_capabilities: [],
    additional_context: '',
  })
  
  // Review depth selection
  const [reviewDepth, setReviewDepth] = useState<'quick_scan' | 'standard' | 'deep_dive'>('standard')

  // Load example prompt from sessionStorage if available
  useEffect(() => {
    const examplePrompt = sessionStorage.getItem('examplePrompt')
    if (examplePrompt) {
      setFormData(prev => ({ 
        ...prev, 
        project_description: examplePrompt,
        project_name: 'My AI Project' // Default name they can change
      }))
      sessionStorage.removeItem('examplePrompt') // Clear after use
    }
  }, [])

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

  // Accessibility: Focus management when section changes
  useEffect(() => {
    if (reviewMode === 'advanced' && sectionRef.current) {
      // Move focus to section heading for screen readers
      sectionRef.current.focus()
      announce(`Step ${currentSection + 1} of ${advancedSections.length}: ${advancedSections[currentSection].title}`)
    }
  }, [currentSection, reviewMode, announce, advancedSections])

  // Accessibility: Focus error message when it appears
  useEffect(() => {
    if (error && errorRef.current) {
      errorRef.current.focus()
      announce(error, 'assertive')
    }
  }, [error, announce])

  // Accessibility: Validate field and return error message if invalid
  const validateField = (fieldName: string, value: string, required: boolean = false): string | null => {
    if (required && !value.trim()) {
      return `${fieldName} is required`
    }
    return null
  }

  // Accessibility: Clear field error when user starts typing
  const clearFieldError = (fieldName: string) => {
    setFieldErrors(prev => prev.filter(e => e.field !== fieldName))
  }

  // Accessibility: Keyboard navigation for wizard
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (reviewMode !== 'advanced') return
    
    // Navigate between sections with Page Up/Down
    if (e.key === 'PageDown' && currentSection < advancedSections.length - 1) {
      e.preventDefault()
      setCurrentSection(prev => prev + 1)
    } else if (e.key === 'PageUp' && currentSection > 0) {
      e.preventDefault()
      setCurrentSection(prev => prev - 1)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      if (reviewMode === 'basic') {
        // Only description is truly required now
        if (!formData.project_description?.trim()) {
          throw new Error('Please describe your AI idea - even a single sentence works!')
        }
        // Include review depth in the description for the AI to understand
        const enhancedFormData = {
          ...formData,
          // Use a default project name if not provided
          project_name: formData.project_name?.trim() || 'My AI Project',
          project_description: `[Review Mode: ${reviewDepth.replace('_', ' ').toUpperCase()}]\n\n${formData.project_description}\n\n` +
            (formData.industry ? `Industry: ${formData.industry}\n` : '') +
            (formData.technology_type ? `Use Case Type: ${formData.technology_type}\n` : '') +
            (formData.target_users ? `Target Users: ${formData.target_users}\n` : '') +
            (formData.data_types ? `Data Sensitivity: ${formData.data_types}\n` : '') +
            (formData.ai_capabilities?.length ? `AI Capabilities/Risk Factors: ${formData.ai_capabilities.join(', ')}\n` : '') +
            (formData.additional_context ? `\nSpecific Questions/Concerns:\n${formData.additional_context}` : '')
        }
        const response = await apiClient.submitReview(enhancedFormData as AIReviewSubmission)
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
    <div className={styles.modeSelectorWrapper}>
      <fieldset className={styles.modeSelector} role="radiogroup" aria-label="Select review type">
        <legend className={styles.visuallyHidden}>Review Type Selection</legend>
        <div className={`${styles.modeCard} ${reviewMode === 'basic' ? styles.modeCardActive : ''}`}>
          <button
            type="button"
            role="radio"
            aria-checked={reviewMode === 'basic'}
            className={`${styles.modeButton} ${reviewMode === 'basic' ? styles.modeActive : ''}`}
            onClick={() => {
              setReviewMode('basic')
              announce('Basic Review selected - quick assessment mode')
            }}
          >
            <span className={styles.modeIcon} aria-hidden="true">⚡</span>
            <div className={styles.modeContent}>
              <span className={styles.modeTitle}>Basic Review</span>
              <span className={styles.modeDesc}>Quick assessment with project name and description</span>
            </div>
          </button>
          
          {/* Speed submenu - only shown when basic is selected */}
          {reviewMode === 'basic' && (
            <div className={styles.speedSubmenu} role="group" aria-label="Review speed options">
              <span className={styles.speedSubmenuLabel}>Analysis Depth:</span>
              <div className={styles.speedSubmenuOptions}>
                <label className={`${styles.speedChip} ${reviewDepth === 'quick_scan' ? styles.speedChipActive : ''}`}>
                  <input
                    type="radio"
                    name="reviewDepth"
                    value="quick_scan"
                    checked={reviewDepth === 'quick_scan'}
                    onChange={() => setReviewDepth('quick_scan')}
                    className={styles.speedRadio}
                  />
                  <span aria-hidden="true">⚡</span> Quick
                </label>
                <label className={`${styles.speedChip} ${reviewDepth === 'standard' ? styles.speedChipActive : ''}`}>
                  <input
                    type="radio"
                    name="reviewDepth"
                    value="standard"
                    checked={reviewDepth === 'standard'}
                    onChange={() => setReviewDepth('standard')}
                    className={styles.speedRadio}
                  />
                  <span aria-hidden="true">📋</span> Standard
                </label>
                <label className={`${styles.speedChip} ${reviewDepth === 'deep_dive' ? styles.speedChipActive : ''}`}>
                  <input
                    type="radio"
                    name="reviewDepth"
                    value="deep_dive"
                    checked={reviewDepth === 'deep_dive'}
                    onChange={() => setReviewDepth('deep_dive')}
                    className={styles.speedRadio}
                  />
                  <span aria-hidden="true">🔬</span> Deep Dive
                </label>
              </div>
            </div>
          )}
        </div>
        
        <div className={`${styles.modeCard} ${reviewMode === 'advanced' ? styles.modeCardActive : ''}`}>
          <button
            type="button"
            role="radio"
            aria-checked={reviewMode === 'advanced'}
            className={`${styles.modeButton} ${reviewMode === 'advanced' ? styles.modeActive : ''}`}
            onClick={() => {
              setReviewMode('advanced')
              announce('Comprehensive Review selected - 10 step questionnaire')
            }}
          >
            <span className={styles.modeIcon} aria-hidden="true">🔬</span>
            <div className={styles.modeContent}>
              <span className={styles.modeTitle}>Comprehensive Review</span>
              <span className={styles.modeDesc}>In-depth analysis with detailed questionnaire</span>
            </div>
          </button>
        </div>
      </fieldset>
    </div>
  )

  // Track which optional sections are expanded
  const [showMoreDetails, setShowMoreDetails] = useState(false)
  const [showRiskFactors, setShowRiskFactors] = useState(false)

  const handleCapabilityToggle = (capabilityId: string) => {
    const current = formData.ai_capabilities || []
    const updated = current.includes(capabilityId)
      ? current.filter(c => c !== capabilityId)
      : [...current, capabilityId]
    setFormData(prev => ({ ...prev, ai_capabilities: updated }))
  }

  // Calculate how complete the form is for the accuracy indicator
  const getFormCompleteness = () => {
    let filled = 0
    let total = 7
    if (formData.project_name) filled++
    if (formData.project_description) filled++
    if (formData.industry) filled++
    if (formData.technology_type) filled++
    if (formData.data_types) filled++
    if (formData.target_users) filled++
    if (formData.ai_capabilities && formData.ai_capabilities.length > 0) filled++
    return Math.round((filled / total) * 100)
  }

  const renderBasicForm = () => (
    <>
      {/* Encouraging intro message */}
      <section className={styles.introSection} aria-labelledby="intro-title">
        <div className={styles.introIcon} aria-hidden="true">💡</div>
        <div className={styles.introContent}>
          <h2 id="intro-title" className={styles.introTitle}>Tell us about your AI idea</h2>
          <p className={styles.introText}>
            <strong>Only one field is required</strong> — just describe what you want to build. 
            The more details you add, the more accurate and tailored our recommendations will be.
          </p>
        </div>
      </section>

      {/* Accuracy Indicator - Accessible progress bar */}
      <div 
        className={styles.accuracyIndicator}
        role="region"
        aria-label="Form completion progress"
      >
        <div className={styles.accuracyHeader}>
          <span id="accuracy-label" className={styles.accuracyLabel}>Recommendation Accuracy</span>
          <span className={styles.accuracyPercent} aria-hidden="true">{getFormCompleteness()}%</span>
        </div>
        <div 
          className={styles.accuracyBar}
          role="progressbar"
          aria-valuenow={getFormCompleteness()}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-labelledby="accuracy-label"
          aria-describedby="accuracy-hint"
        >
          <div 
            className={styles.accuracyFill} 
            style={{ width: `${getFormCompleteness()}%` }}
          />
        </div>
        <p id="accuracy-hint" className={styles.accuracyHint}>
          {getFormCompleteness() < 30 && "Add more details to improve recommendations"}
          {getFormCompleteness() >= 30 && getFormCompleteness() < 60 && "Good start! A few more details will help"}
          {getFormCompleteness() >= 60 && getFormCompleteness() < 85 && "Great! We have enough for solid recommendations"}
          {getFormCompleteness() >= 85 && "Excellent! You'll get highly tailored guidance"}
        </p>
      </div>

      {/* Main Input - The Only Required Field */}
      <section className={styles.section} aria-labelledby="main-input-label">
        <div className={styles.formGroup}>
          <label id="main-input-label" htmlFor="project-description" className={styles.label}>
            Describe your AI idea <span className={styles.required} aria-label="required">*</span>
          </label>
          <textarea
            id="project-description"
            name="project_description"
            value={formData.project_description}
            onChange={(e) => {
              setFormData(prev => ({ ...prev, project_description: e.target.value }))
              clearFieldError('project_description')
            }}
            className={`${styles.textareaLarge} ${fieldErrors.some(e => e.field === 'project_description') ? styles.inputError : ''}`}
            rows={6}
            aria-required="true"
            aria-describedby="description-hint description-error"
            aria-invalid={fieldErrors.some(e => e.field === 'project_description')}
            autoComplete="off"
            placeholder="Just tell us what you're trying to build. For example:

• 'We want to create a chatbot that answers customer questions about our products'
• 'I'm thinking about using AI to help screen job applications'
• 'We need to summarize long legal documents for our team'
• 'I want to build an AI tutor for students'

Don't worry about technical details - we'll help you figure those out!"
          />
          {fieldErrors.some(e => e.field === 'project_description') && (
            <div id="description-error" className={styles.fieldError} role="alert">
              {fieldErrors.find(e => e.field === 'project_description')?.message}
            </div>
          )}
          <div id="description-hint" className={styles.inputHintLight}>
            <span aria-hidden="true">✨</span> Tip: Even a single sentence is enough to get started!
          </div>
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="project-name" className={styles.label}>
            Project Name <span className={styles.optional}>(optional)</span>
          </label>
          <input
            id="project-name"
            type="text"
            name="project_name"
            value={formData.project_name}
            onChange={(e) => setFormData(prev => ({ ...prev, project_name: e.target.value }))}
            className={styles.input}
            autoComplete="off"
            placeholder="Give your project a name, or we'll use 'My AI Project'"
          />
        </div>
      </section>

      {/* Quick Context - Optional but helpful */}
      <section className={styles.section} aria-labelledby="quick-context-title">
        <div className={styles.sectionHeaderCollapsible}>
          <div>
            <h2 id="quick-context-title" className={styles.sectionTitle}>
              <span aria-hidden="true">🎯</span> Quick Context
            </h2>
            <p className={styles.sectionDescription}>
              These help us give you industry-specific guidance
            </p>
          </div>
          <span className={styles.optionalBadge}>Optional</span>
        </div>

        <div className={styles.quickContextGrid} role="group" aria-label="Quick context options">
          <div className={styles.contextCard}>
            <label htmlFor="industry-select" className={styles.contextLabel}>Industry</label>
            <select
              id="industry-select"
              name="industry"
              value={formData.industry || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, industry: e.target.value }))}
              className={styles.selectCompact}
              aria-describedby="industry-help"
            >
              {INDUSTRY_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <span id="industry-help" className={styles.contextHelp}>Helps with compliance requirements</span>
          </div>

          <div className={styles.contextCard}>
            <label htmlFor="technology-select" className={styles.contextLabel}>Type of AI</label>
            <select
              id="technology-select"
              name="technology_type"
              value={formData.technology_type || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, technology_type: e.target.value }))}
              className={styles.selectCompact}
              aria-describedby="technology-help"
            >
              {USE_CASE_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <span id="technology-help" className={styles.contextHelp}>Helps suggest reference architectures</span>
          </div>

          <div className={styles.contextCard}>
            <label htmlFor="data-sensitivity-select" className={styles.contextLabel}>Data Sensitivity</label>
            <select
              id="data-sensitivity-select"
              name="data_types"
              value={formData.data_types || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, data_types: e.target.value }))}
              className={styles.selectCompact}
              aria-describedby="data-help"
            >
              {DATA_SENSITIVITY_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <span id="data-help" className={styles.contextHelp}>Helps with privacy recommendations</span>
          </div>

          <div className={styles.contextCard}>
            <label htmlFor="stage-select" className={styles.contextLabel}>Project Stage</label>
            <select
              id="stage-select"
              name="deployment_stage"
              value={formData.deployment_stage}
              onChange={(e) => setFormData(prev => ({ ...prev, deployment_stage: e.target.value }))}
              className={styles.selectCompact}
              aria-describedby="stage-help"
            >
              <option value="Planning">💡 Just an idea</option>
              <option value="Development">🔧 Building it</option>
              <option value="Testing">🧪 Testing</option>
              <option value="Production">🚀 Already live</option>
            </select>
            <span id="stage-help" className={styles.contextHelp}>Helps prioritize recommendations</span>
          </div>
        </div>
      </section>

      {/* Expandable: More Details */}
      <section className={styles.expandableSection} aria-labelledby="more-details-heading">
        <button 
          type="button"
          className={styles.expandButton}
          onClick={() => setShowMoreDetails(!showMoreDetails)}
          aria-expanded={showMoreDetails}
          aria-controls="more-details-content"
        >
          <span className={styles.expandIcon} aria-hidden="true">{showMoreDetails ? '▼' : '▶'}</span>
          <span id="more-details-heading" className={styles.expandTitle}>Add more details</span>
          <span className={styles.expandBadge} aria-label="improves accuracy by 15 percent">+15% accuracy</span>
        </button>
        
        {showMoreDetails && (
          <div id="more-details-content" className={styles.expandContent}>
            <div className={styles.formGroup}>
              <label htmlFor="target-users" className={styles.label}>
                Who will use this AI? <span className={styles.optional}>(optional)</span>
              </label>
              <input
                id="target-users"
                type="text"
                name="target_users"
                value={formData.target_users || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, target_users: e.target.value }))}
                className={styles.input}
                autoComplete="off"
                placeholder="e.g., Customers, employees, students, healthcare providers..."
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="additional-context" className={styles.label}>
                Any specific questions or concerns? <span className={styles.optional}>(optional)</span>
              </label>
              <textarea
                id="additional-context"
                name="additional_context"
                value={formData.additional_context || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, additional_context: e.target.value }))}
                className={styles.textarea}
                rows={3}
                placeholder="e.g., How do we prevent bias? What about GDPR? Is this use case allowed under EU AI Act?"
              />
            </div>
          </div>
        )}
      </section>

      {/* Expandable: Risk Factors */}
      <section className={styles.expandableSection} aria-labelledby="risk-factors-heading">
        <button 
          type="button"
          className={styles.expandButton}
          onClick={() => setShowRiskFactors(!showRiskFactors)}
          aria-expanded={showRiskFactors}
          aria-controls="risk-factors-content"
        >
          <span className={styles.expandIcon} aria-hidden="true">{showRiskFactors ? '▼' : '▶'}</span>
          <span id="risk-factors-heading" className={styles.expandTitle}>Identify risk factors</span>
          <span className={styles.expandBadge} aria-label="improves accuracy by 20 percent">+20% accuracy</span>
        </button>
        
        {showRiskFactors && (
          <div id="risk-factors-content" className={styles.expandContent}>
            <p id="risk-factors-description" className={styles.expandDescription}>
              Check any that apply to your AI system. This helps us identify potential compliance requirements and risks.
            </p>
            <div className={styles.riskGrid} role="group" aria-labelledby="risk-factors-heading" aria-describedby="risk-factors-description">
              {AI_CAPABILITIES.map(cap => (
                <label
                  key={cap.id}
                  className={`${styles.riskItem} ${
                    formData.ai_capabilities?.includes(cap.id) ? styles.riskItemSelected : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={formData.ai_capabilities?.includes(cap.id) || false}
                    onChange={() => handleCapabilityToggle(cap.id)}
                    className={styles.riskCheckbox}
                  />
                  <span className={styles.riskLabel}>{cap.label}</span>
                </label>
              ))}
            </div>
          </div>
        )}
      </section>
    </>
  )

  const renderAdvancedSection = (sectionIndex: number) => {
    const section = advancedSections[sectionIndex]
    
    return (
      <section 
        ref={sectionRef}
        className={styles.section}
        tabIndex={-1}
        aria-labelledby={`section-title-${sectionIndex}`}
      >
        <div className={styles.sectionHeader}>
          <span className={styles.sectionIcon} aria-hidden="true">{section.icon}</span>
          <div>
            <h2 id={`section-title-${sectionIndex}`} className={styles.sectionTitle}>{section.title}</h2>
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
    <nav 
      className={styles.progressContainer}
      aria-label="Form progress"
      role="navigation"
    >
      <div 
        className={styles.progressBar}
        role="tablist"
        aria-label="Review sections"
      >
        {advancedSections.map((section, index) => (
          <button
            key={index}
            type="button"
            role="tab"
            aria-selected={index === currentSection}
            aria-label={`Step ${index + 1}: ${section.title}${index < currentSection ? ' (completed)' : ''}`}
            className={`${styles.progressStep} ${index === currentSection ? styles.progressActive : ''} ${index < currentSection ? styles.progressComplete : ''}`}
            onClick={() => {
              setCurrentSection(index)
              announce(`Navigated to step ${index + 1}: ${section.title}`)
            }}
          >
            <span className={styles.progressIcon} aria-hidden="true">{section.icon}</span>
          </button>
        ))}
      </div>
      <div className={styles.progressLabel} aria-live="polite">
        <span className={styles.visuallyHidden}>Current step: </span>
        {advancedSections[currentSection].title}
      </div>
    </nav>
  )

  const renderAdvancedNavigation = () => (
    <div 
      className={styles.navigationButtons}
      role="navigation"
      aria-label="Form navigation"
    >
      <button
        type="button"
        onClick={() => {
          setCurrentSection(prev => prev - 1)
          announce(`Going to previous step`)
        }}
        disabled={currentSection === 0}
        className={styles.navButton}
        aria-label={currentSection > 0 ? `Go to previous step: ${advancedSections[currentSection - 1]?.title}` : 'Previous (disabled - at first step)'}
      >
        <span aria-hidden="true">←</span> Previous
      </button>
      <span className={styles.stepIndicator} aria-live="polite">
        <span className={styles.visuallyHidden}>Step </span>
        {currentSection + 1} <span className={styles.visuallyHidden}>of</span><span aria-hidden="true">/</span> {advancedSections.length}
      </span>
      {currentSection < advancedSections.length - 1 ? (
        <button
          type="button"
          onClick={() => {
            setCurrentSection(prev => prev + 1)
            announce(`Going to next step`)
          }}
          className={styles.navButton}
          aria-label={`Go to next step: ${advancedSections[currentSection + 1]?.title}`}
        >
          Next <span aria-hidden="true">→</span>
        </button>
      ) : (
        <button
          type="submit"
          disabled={loading}
          className={styles.submitButton}
          aria-busy={loading}
          aria-label={loading ? 'Analyzing your submission, please wait' : 'Submit form to get AI recommendations'}
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
                        {tool.name} <span aria-hidden="true">↗</span>
                        <span className={styles.visuallyHidden}>(opens in new tab)</span>
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
      {/* Screen reader live region for announcements */}
      <div 
        ref={announcerRef}
        className={styles.visuallyHidden}
        aria-live="polite"
        aria-atomic="true"
        role="status"
      />
      
      <a href="#main-form" className={styles.skipLink}>
        Skip to main form
      </a>
      
      <header className={styles.header} role="banner">
        <button 
          onClick={() => router.push('/')} 
          className={styles.backButton}
          aria-label="Go back to home page"
        >
          <span aria-hidden="true">←</span> Back to Home
        </button>
        <h1 className={styles.title}>AI Solution Review</h1>
        <p className={styles.subtitle}>
          Get instant Responsible AI recommendations powered by Azure OpenAI
        </p>
      </header>

      {!result ? (
        <form 
          id="main-form"
          ref={formRef}
          onSubmit={handleSubmit} 
          className={styles.form}
          onKeyDown={handleKeyDown}
          aria-label="AI Solution Review Form"
          noValidate
        >
          {error && (
            <div 
              ref={errorRef}
              className={styles.error}
              role="alert"
              aria-live="assertive"
              tabIndex={-1}
            >
              <span className={styles.visuallyHidden}>Error: </span>
              {error}
            </div>
          )}

          {renderModeSelector()}

          {reviewMode === 'basic' ? (
            <>
              {renderBasicForm()}
              <div className={styles.submitSection} role="group" aria-label="Form actions">
                <button
                  type="submit"
                  disabled={loading}
                  className={styles.submitButton}
                  aria-busy={loading}
                  aria-label={loading ? 'Analyzing your submission, please wait' : 'Submit form to get AI recommendations'}
                >
                  {loading ? 'Analyzing with AI...' : 'Get AI Recommendations'}
                </button>
                <button
                  type="button"
                  onClick={() => router.push('/')}
                  className={styles.cancelButton}
                  aria-label="Cancel and return to home page"
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

            {/* Risk Scores Section */}
            {result.risk_scores && (
              <div className={styles.riskScoresSection}>
                <h3 className={styles.sectionHeading}>📊 Risk Assessment</h3>
                <div className={styles.riskScoreMain}>
                  <div className={styles.overallRiskScore}>
                    <div className={`${styles.riskScoreCircle} ${styles[`risk${result.risk_scores.risk_level?.replace(' ', '')}`]}`}>
                      <span className={styles.riskScoreNumber}>{result.risk_scores.overall_score}</span>
                      <span className={styles.riskScoreLabel}>/ 100</span>
                    </div>
                    <span className={`${styles.riskLevel} ${styles[`risk${result.risk_scores.risk_level?.replace(' ', '')}`]}`}>
                      {result.risk_scores.risk_level} Risk
                    </span>
                  </div>
                  {result.risk_scores.score_explanation && (
                    <p className={styles.riskExplanation}>{result.risk_scores.score_explanation}</p>
                  )}
                </div>
                {result.risk_scores.principle_scores && (
                  <div className={styles.principleScores}>
                    <h4>Scores by Principle</h4>
                    <div className={styles.principleScoreGrid}>
                      <div className={styles.principleScoreItem}>
                        <span className={styles.principleName}>Fairness</span>
                        <div className={styles.scoreBar}>
                          <div className={styles.scoreBarFill} style={{width: `${result.risk_scores.principle_scores.fairness}%`}}></div>
                        </div>
                        <span className={styles.scoreValue}>{result.risk_scores.principle_scores.fairness}</span>
                      </div>
                      <div className={styles.principleScoreItem}>
                        <span className={styles.principleName}>Reliability & Safety</span>
                        <div className={styles.scoreBar}>
                          <div className={styles.scoreBarFill} style={{width: `${result.risk_scores.principle_scores.reliability_safety}%`}}></div>
                        </div>
                        <span className={styles.scoreValue}>{result.risk_scores.principle_scores.reliability_safety}</span>
                      </div>
                      <div className={styles.principleScoreItem}>
                        <span className={styles.principleName}>Privacy & Security</span>
                        <div className={styles.scoreBar}>
                          <div className={styles.scoreBarFill} style={{width: `${result.risk_scores.principle_scores.privacy_security}%`}}></div>
                        </div>
                        <span className={styles.scoreValue}>{result.risk_scores.principle_scores.privacy_security}</span>
                      </div>
                      <div className={styles.principleScoreItem}>
                        <span className={styles.principleName}>Inclusiveness</span>
                        <div className={styles.scoreBar}>
                          <div className={styles.scoreBarFill} style={{width: `${result.risk_scores.principle_scores.inclusiveness}%`}}></div>
                        </div>
                        <span className={styles.scoreValue}>{result.risk_scores.principle_scores.inclusiveness}</span>
                      </div>
                      <div className={styles.principleScoreItem}>
                        <span className={styles.principleName}>Transparency</span>
                        <div className={styles.scoreBar}>
                          <div className={styles.scoreBarFill} style={{width: `${result.risk_scores.principle_scores.transparency}%`}}></div>
                        </div>
                        <span className={styles.scoreValue}>{result.risk_scores.principle_scores.transparency}</span>
                      </div>
                      <div className={styles.principleScoreItem}>
                        <span className={styles.principleName}>Accountability</span>
                        <div className={styles.scoreBar}>
                          <div className={styles.scoreBarFill} style={{width: `${result.risk_scores.principle_scores.accountability}%`}}></div>
                        </div>
                        <span className={styles.scoreValue}>{result.risk_scores.principle_scores.accountability}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* EU AI Act Classification */}
            {result.eu_ai_act_classification && (
              <div className={styles.euAiActSection}>
                <h3 className={styles.sectionHeading}>🇪🇺 EU AI Act Classification</h3>
                <div className={`${styles.euRiskCategory} ${styles[`euRisk${result.eu_ai_act_classification.risk_category?.replace(' ', '')}`]}`}>
                  <span className={styles.euRiskLabel}>{result.eu_ai_act_classification.risk_category} Risk</span>
                  {result.eu_ai_act_classification.annex_reference && (
                    <span className={styles.euAnnexRef}>{result.eu_ai_act_classification.annex_reference}</span>
                  )}
                </div>
                <p className={styles.euRationale}>{result.eu_ai_act_classification.category_rationale}</p>
                {result.eu_ai_act_classification.compliance_requirements && result.eu_ai_act_classification.compliance_requirements.length > 0 && (
                  <div className={styles.euRequirements}>
                    <h4>Compliance Requirements</h4>
                    <ul>
                      {result.eu_ai_act_classification.compliance_requirements.map((req, i) => (
                        <li key={i}>{req}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.eu_ai_act_classification.estimated_compliance_level && (
                  <div className={styles.complianceLevel}>
                    <strong>Estimated Compliance:</strong> {result.eu_ai_act_classification.estimated_compliance_level}
                  </div>
                )}
                {result.eu_ai_act_classification.compliance_gaps && result.eu_ai_act_classification.compliance_gaps.length > 0 && (
                  <div className={styles.complianceGaps}>
                    <h4>Compliance Gaps to Address</h4>
                    <ul>
                      {result.eu_ai_act_classification.compliance_gaps.map((gap, i) => (
                        <li key={i}>{gap}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Reference Architecture */}
            {result.reference_architecture && (
              <div className={styles.refArchSection}>
                <h3 className={styles.sectionHeading}>🏗️ Recommended Architecture</h3>
                <div className={styles.archPattern}>
                  <h4>{result.reference_architecture.recommended_pattern}</h4>
                  {result.reference_architecture.deployment_complexity && (
                    <span className={styles.archComplexity}>
                      Complexity: {result.reference_architecture.deployment_complexity}
                    </span>
                  )}
                  {result.reference_architecture.estimated_monthly_cost && (
                    <span className={styles.archCost}>
                      Est. Cost: {result.reference_architecture.estimated_monthly_cost}
                    </span>
                  )}
                </div>
                {result.reference_architecture.architecture_diagram && (
                  <div className={styles.archDiagram}>
                    <pre>{result.reference_architecture.architecture_diagram}</pre>
                  </div>
                )}
                {result.reference_architecture.azure_services && result.reference_architecture.azure_services.length > 0 && (
                  <div className={styles.azureServices}>
                    <h4>Azure Services</h4>
                    <div className={styles.serviceGrid}>
                      {result.reference_architecture.azure_services.map((service, i) => (
                        <div key={i} className={styles.serviceCard}>
                          <span className={styles.serviceName}>{service.service}</span>
                          <span className={styles.servicePurpose}>{service.purpose}</span>
                          {service.tier && <span className={styles.serviceTier}>{service.tier}</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {result.reference_architecture.github_repos && result.reference_architecture.github_repos.length > 0 && (
                  <div className={styles.githubRepos}>
                    <h4>📦 Starter Repositories</h4>
                    <div className={styles.repoGrid}>
                      {result.reference_architecture.github_repos.map((repo, i) => (
                        <a key={i} href={repo.url} target="_blank" rel="noopener noreferrer" className={styles.repoCard}>
                          <span className={styles.repoName}>{repo.name}</span>
                          <span className={styles.repoDesc}>{repo.description}</span>
                          <span className={styles.repoLink}>View on GitHub ↗</span>
                        </a>
                      ))}
                    </div>
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
