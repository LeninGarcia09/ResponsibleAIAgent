// API client for communicating with the backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:7071/api'

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

// AI-powered recommendation format
export interface AIRecommendation {
  id: string
  principle: string
  priority: string
  title: string
  issue: string
  recommendation: string
  implementation_steps: string[]
  tools: Tool[]
  effort?: string
  impact?: string
}

// Union type for both formats
export type Recommendation = StaticRecommendation | AIRecommendation

// Check if recommendation is AI format
export function isAIRecommendation(rec: Recommendation): rec is AIRecommendation {
  return 'title' in rec && 'implementation_steps' in rec
}

export interface OverallAssessment {
  summary: string
  maturity_level: string
  key_strengths: string[]
  critical_gaps: string[]
}

// Quick-start guide types for actionable guidance
export interface ChecklistItem {
  task: string
  resource_url?: string
  priority: string
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

export interface QuickStartGuide {
  week_one_checklist?: ChecklistItem[]
  essential_tools?: EssentialTool[]
  thirty_day_roadmap?: {
    week_1?: WeekFocus
    week_2?: WeekFocus
    week_3?: WeekFocus
    week_4?: WeekFocus
  }
  quick_reference?: QuickReference
  templates_and_checklists?: TemplateItem[]
}

export interface ReferenceLink {
  title: string
  url: string
  description: string
}

export interface ReferenceLinks {
  getting_started?: ReferenceLink[]
  tools_documentation?: ReferenceLink[]
  templates?: ReferenceLink[]
}

export interface SubmissionResponse {
  message?: string
  submission_id: string
  project_name: string
  status?: string
  ai_powered?: boolean
  overall_assessment?: OverallAssessment
  quick_start_guide?: QuickStartGuide
  recommendations: Recommendation[]
  summary: {
    total_recommendations: number
    critical_items: number
    high_priority_items: number
    medium_priority_items?: number
    low_priority_items?: number
    top_3_priorities?: string[]
  }
  next_steps?: string[]
  reference_links?: ReferenceLinks
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
