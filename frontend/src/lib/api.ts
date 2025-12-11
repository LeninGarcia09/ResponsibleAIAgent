// API client for communicating with the backend
// Default to the deployed API if env var is missing to avoid "Failed to fetch" in hosted builds
const DEFAULT_REMOTE_API = 'https://rai-backend.graymoss-a8a3aef8.westus3.azurecontainerapps.io/api'
const API_BASE_URL =
  (process.env.NEXT_PUBLIC_API_BASE_URL || '').trim() ||
  // Use local backend for localhost, otherwise fall back to the remote API
  (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8080/api'
    : DEFAULT_REMOTE_API)

if (!process.env.NEXT_PUBLIC_API_BASE_URL) {
  // Surface a clear hint in the console when the env var is not set
  // (helps diagnose production builds pulling the localhost default)
  // eslint-disable-next-line no-console
  console.warn(`NEXT_PUBLIC_API_BASE_URL not set; using ${API_BASE_URL}`)
}

export interface AIReviewSubmission {
  submitter_email?: string
  submitter_name?: string
  project_name: string
  project_description?: string
  ai_capabilities?: string[]
  data_sources?: string[]
  user_impact?: string
  deployment_stage?: string
  technology_type?: string
  industry?: string
  target_users?: string
  data_types?: string
  additional_context?: string
}

// Advanced review submission with comprehensive questionnaire
export interface AdvancedReviewSubmission {
  project_name: string
  deployment_stage?: string
  // Purpose & Use Case
  intended_purpose?: string
  business_problem?: string
  end_users?: string
  // Data & Inputs
  data_sources?: string
  data_collection_storage?: string
  sensitive_data?: string
  // Model & Technology
  ai_models?: string
  model_type?: string
  environments_connectors?: string
  // Fairness & Bias
  bias_checking?: string
  bias_mitigation?: string
  // Transparency & Explainability
  decision_explainability?: string
  output_documentation?: string
  // Accountability & Governance
  system_ownership?: string
  escalation_paths?: string
  // Security & Privacy
  data_security?: string
  privacy_compliance?: string
  // Impact & Risk
  potential_risks?: string
  risk_monitoring?: string
  // User Interaction
  user_interaction_method?: string
  human_in_loop?: string
}

// Tool reference with URL
export interface Tool {
  name: string
  url: string
  description?: string
  purpose?: string
  category?: string
  install?: string
}

// Simple recommendation format (from quick guidance API)
export interface SimpleRecommendation {
  priority: string
  recommendation?: string
  description?: string  // API sometimes returns description instead of recommendation
}

// Static format recommendation (fallback)
export interface StaticRecommendation {
  principle: string
  priority: string
  description?: string
  key_questions?: string[]
  recommendations: string[]
  tools?: Tool[]
}

// Code example in recommendation
export interface CodeExample {
  language: string
  code: string
  explanation?: string
}

// AI-powered recommendation format (enhanced v2)
export interface AIRecommendation {
  id: string
  principle: string
  priority: string
  title: string
  issue: string
  recommendation: string
  implementation_steps: string[]
  code_example?: CodeExample
  tools: Tool[]
  effort?: string
  time_estimate?: string
  skill_required?: string
  impact?: string
  confidence?: string
  alternatives?: string[]
}

// Tiered recommendation item (v4.0 - world-class tier system)
export interface TieredRecommendationItem {
  id: string
  title: string
  description: string
  tier_label: string  // "🚨 NON-NEGOTIABLE", "⚠️ HIGHLY RECOMMENDED", etc.
  tier_reason: string
  skip_risk: string
  implementation_deadline?: string  // "Before any deployment", "Within 2 weeks", etc.
  tools: Tool[]
  implementation_steps?: string[]
  time_estimate?: string
  effort?: string
}

// Tier summary statistics
export interface TierSummary {
  non_negotiable_count: number
  highly_recommended_count: number
  recommended_count: number
  optional_count: number
  deployment_readiness: string  // "Blocked", "At Risk", "Mostly Ready", "Ready"
  readiness_explanation: string
}

// Tiered recommendations container
export interface TieredRecommendations {
  non_negotiable: TieredRecommendationItem[]
  highly_recommended: TieredRecommendationItem[]
  recommended: TieredRecommendationItem[]
  optional: TieredRecommendationItem[]
  tier_summary?: TierSummary
}

// Pillar-based recommendation item
export interface PillarRecommendationItem {
  title: string
  why_needed: string
  what_happens_without: string
  priority: string
  tier?: string
  tool?: {
    name: string
    url: string
    purpose?: string
    how_it_helps?: string
  }
  implementation_steps?: string[]
}

// Single pillar recommendations
export interface PillarRecommendations {
  pillar_name: string
  pillar_icon?: string
  pillar_description?: string
  why_it_matters: string
  risk_if_ignored?: string
  recommendations: PillarRecommendationItem[]
}

// All pillars grouped
export interface RecommendationsByPillar {
  fairness?: PillarRecommendations
  reliability_safety?: PillarRecommendations
  privacy_security?: PillarRecommendations
  inclusiveness?: PillarRecommendations
  transparency?: PillarRecommendations
  accountability?: PillarRecommendations
}

// Union type for all recommendation formats
export type Recommendation = SimpleRecommendation | StaticRecommendation | AIRecommendation

// Check if recommendation is AI format (detailed with steps)
export function isAIRecommendation(rec: Recommendation): rec is AIRecommendation {
  return 'title' in rec && 'implementation_steps' in rec
}

// Check if recommendation is simple format (just priority + recommendation/description text)
export function isSimpleRecommendation(rec: Recommendation): rec is SimpleRecommendation {
  return ('recommendation' in rec || 'description' in rec) && !('title' in rec) && !('principle' in rec) && !('recommendations' in rec)
}

export interface OverallAssessment {
  summary: string
  maturity_level: string
  key_strengths: string[]
  critical_gaps: string[]
}

// Risk Scores (new in v2, enhanced in v3)
export interface PrincipleScores {
  fairness: number
  reliability_safety: number
  privacy_security: number
  inclusiveness: number
  transparency: number
  accountability: number
}

// Score driver for risk factors
export interface ScoreDriver {
  factor: string
  impact: string
  severity?: string  // Low | Medium | High | Critical (for negative drivers)
}

// Critical factors affecting the score
export interface CriticalFactors {
  score_drivers_positive: ScoreDriver[]
  score_drivers_negative: ScoreDriver[]
}

// Qualitative assessment level
export interface QualitativeLevel {
  level: string  // Low | Medium | High
  rationale: string
}

// Qualitative risk assessment
export interface QualitativeAssessment {
  data_sensitivity: QualitativeLevel
  user_impact: QualitativeLevel
  regulatory_exposure: QualitativeLevel
  technical_complexity: QualitativeLevel
  deployment_readiness: QualitativeLevel
}

export interface RiskScores {
  overall_score: number
  risk_level: string
  risk_summary?: string  // High-level description of risk posture
  critical_factors?: CriticalFactors
  qualitative_assessment?: QualitativeAssessment
  principle_scores: PrincipleScores
  score_explanation?: string
}

// EU AI Act Classification (new in v2)
export interface EUAIActClassification {
  risk_category: string
  category_rationale: string
  annex_reference?: string
  compliance_requirements: string[]
  estimated_compliance_level: string
  compliance_gaps: string[]
}

// Reference Architecture (new in v2)
export interface AzureService {
  service: string
  purpose: string
  tier?: string
}

export interface GitHubRepo {
  name: string
  url: string
  description: string
}

export interface ReferenceArchitecture {
  recommended_pattern: string
  architecture_diagram?: string
  azure_services: AzureService[]
  github_repos: GitHubRepo[]
  deployment_complexity?: string
}

// Quick-start guide types for actionable guidance (enhanced v2)
export interface ChecklistItem {
  task: string
  resource_url?: string
  priority: string
  time_estimate?: string
}

export interface EssentialTool {
  name: string
  url: string
  install_command?: string
  purpose: string
}

export interface WeekFocus {
  focus: string
  actions: string[]
  milestone?: string
}

export interface QuickReference {
  top_3_tools: string[]
  key_metrics: string[]
  red_flags: string[]
  stakeholders_to_involve: string[]
}

export interface TemplateItem {
  name: string
  url: string
  purpose: string
}

export interface CodeSnippet {
  tool: string
  description: string
  language: string
  code: string
}

export interface QuickStartGuide {
  detected_project_type?: string
  week_one_checklist?: ChecklistItem[]
  essential_tools?: EssentialTool[]
  thirty_day_roadmap?: {
    week_1?: WeekFocus
    week_2?: WeekFocus
    week_3?: WeekFocus
    week_4?: WeekFocus
  }
  quick_reference?: QuickReference
  code_snippets?: CodeSnippet[]
  templates_and_checklists?: TemplateItem[]
}

export interface ReferenceLink {
  title: string
  url: string
  description: string
}

export interface ReferenceLinks {
  getting_started?: ReferenceLink[]
  architecture_references?: ReferenceLink[]
  tools_documentation?: ReferenceLink[]
  templates?: ReferenceLink[]
  github_repositories?: ReferenceLink[]
}

// Self-evaluation from agent (new in v2)
export interface SelfEvaluation {
  response_confidence: string
  limitations: string[]
  additional_info_needed: string[]
  follow_up_questions: string[]
}

export interface SubmissionResponse {
  message?: string
  submission_id: string
  project_name: string
  status?: string
  ai_powered?: boolean
  review_mode?: string  // quick_scan | standard | deep_dive
  overall_assessment?: OverallAssessment
  risk_scores?: RiskScores
  eu_ai_act_classification?: EUAIActClassification
  reference_architecture?: ReferenceArchitecture
  quick_start_guide?: QuickStartGuide
  recommendations?: Recommendation[]  // Made optional - AI might not return this
  tiered_recommendations?: TieredRecommendations  // v4.0 tiered system
  recommendations_by_pillar?: RecommendationsByPillar  // v5.0 pillar-organized recommendations
  summary?: {  // Made optional - AI might not return this
    total_recommendations: number
    critical_items: number
    high_priority_items: number
    medium_priority_items?: number
    low_priority_items?: number
    top_3_priorities?: string[]
    estimated_total_effort?: string
  }
  next_steps?: string[]
  reference_links?: ReferenceLinks
  self_evaluation?: SelfEvaluation
  microsoft_rai_resources?: {
    overview: string
    standards: string
    tools: string
  }
}

export interface ReviewResponse {
  message: string
  review_id: string
  overall_status: string
  overall_score: number
}

export interface ReportResponse {
  message: string
  review_id: string
  report_url: string
}

class APIClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = this.baseURL + endpoint

    const defaultHeaders = {
      'Content-Type': 'application/json',
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.error || 'HTTP error! status: ' + response.status
        )
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Submit a new AI solution for review (basic)
  async submitReview(data: AIReviewSubmission): Promise<SubmissionResponse> {
    return this.request<SubmissionResponse>('/submit-review', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Submit comprehensive review with detailed questionnaire
  async submitAdvancedReview(data: AdvancedReviewSubmission): Promise<SubmissionResponse> {
    return this.request<SubmissionResponse>('/submit-advanced-review', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Process/start review for a submission
  async processReview(submissionId: string): Promise<ReviewResponse> {
    return this.request<ReviewResponse>('/process-review', {
      method: 'POST',
      body: JSON.stringify({ submission_id: submissionId }),
    })
  }

  // Generate report for a completed review
  async generateReport(reviewId: string): Promise<ReportResponse> {
    return this.request<ReportResponse>('/generate-report', {
      method: 'POST',
      body: JSON.stringify({ review_id: reviewId }),
    })
  }

  // Get review status
  async getReviewStatus(submissionId: string): Promise<any> {
    return this.request('/review-status/' + submissionId, {
      method: 'GET',
    })
  }

  // Health check
  async healthCheck(): Promise<any> {
    return this.request('/health', {
      method: 'GET',
    })
  }
}

// Export singleton instance
export const apiClient = new APIClient()

// Export class for custom instances
export default APIClient
