'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import styles from './catalog.module.css'

// Types matching the backend knowledge structure
interface ToolCapabilities {
  [key: string]: string[] | undefined
}

interface Tool {
  name: string
  type?: string
  status?: string
  announced?: string
  description: string
  capabilities?: ToolCapabilities | string[]
  integration_points?: string[]
  use_cases?: string[]
  documentation_url?: string
  github_url?: string
  install?: string
  url?: string
  category?: string
}

interface CategoryData {
  description: string
  tools: Tool[]
}

interface CategoriesMap {
  [key: string]: CategoryData
}

interface QuickReferenceItem {
  tools: string[]
  first_action: string
  documentation: string
}

interface QuickReference {
  description?: string
  tool_by_risk?: { [key: string]: QuickReferenceItem | string[] }
  minimum_viable_rai?: object
}

interface ResourceLink {
  title: string
  url: string
  description: string
  status?: string
}

interface ResourceCategory {
  [key: string]: ResourceLink
}

interface ResourcesData {
  core_documentation?: ResourceCategory
  microsoft_foundry?: ResourceCategory & { note?: string }
  content_safety?: ResourceCategory
  evaluation?: ResourceCategory
  fairness?: ResourceCategory
  explainability?: ResourceCategory
  privacy?: ResourceCategory
  security?: ResourceCategory
  design?: ResourceCategory
  reference_architectures?: ResourceCategory
}

interface CatalogMetadata {
  version?: string
  last_updated?: string
  ignite_2025_updates?: boolean
}

interface UseCaseTool {
  tool: string
  purpose: string
  configuration?: string
}

interface UseCase {
  id: string
  title: string
  description: string
  industry_relevance: string[]
  risk_profile: string
  required_tools: UseCaseTool[]
  recommended_tools?: UseCaseTool[]
  implementation_steps: string[]
  success_metrics: string[]
  common_pitfalls: string[]
}

interface UseCasesData {
  description: string
  scenarios: UseCase[]
}

interface ToolsApiResponse {
  tools: CategoriesMap
  quick_reference?: QuickReference
  client_framework?: object
  metadata?: CatalogMetadata
  use_cases?: UseCasesData
  source: string
}

// Category display configuration with icons and friendly names
const categoryConfig: { [key: string]: { title: string; icon: string; order: number } } = {
  governance_and_control: { title: 'Governance & Control', icon: '🏛️', order: 1 },
  content_safety: { title: 'Content Safety', icon: '🛡️', order: 2 },
  evaluation_and_testing: { title: 'Evaluation & Testing', icon: '🧪', order: 3 },
  fairness_and_bias: { title: 'Fairness & Bias', icon: '⚖️', order: 4 },
  explainability_and_interpretability: { title: 'Explainability & Interpretability', icon: '🔍', order: 5 },
  privacy: { title: 'Privacy', icon: '🔒', order: 6 },
  design_and_ux: { title: 'Design & UX', icon: '🎨', order: 7 },
  agent_development: { title: 'Agent Development', icon: '🤖', order: 8 },
  security_integration: { title: 'Security Integration', icon: '🔐', order: 9 },
  // Fallbacks for old-style categories
  fairness: { title: 'Fairness & Bias Mitigation', icon: '⚖️', order: 10 },
  transparency: { title: 'Transparency & Explainability', icon: '🔍', order: 11 },
  safety: { title: 'Reliability & Safety', icon: '🛡️', order: 12 },
  security: { title: 'Security', icon: '🔐', order: 13 },
  accountability: { title: 'Accountability & Governance', icon: '📋', order: 14 },
  llm_specific: { title: 'LLM & Generative AI', icon: '🧠', order: 15 },
}

// Resources category configuration
const resourceCategoryConfig: { [key: string]: { title: string; icon: string; order: number } } = {
  core_documentation: { title: 'Core Documentation', icon: '📚', order: 1 },
  microsoft_foundry: { title: 'Microsoft Foundry', icon: '🏗️', order: 2 },
  content_safety: { title: 'Content Safety', icon: '🛡️', order: 3 },
  evaluation: { title: 'Evaluation', icon: '🧪', order: 4 },
  fairness: { title: 'Fairness', icon: '⚖️', order: 5 },
  explainability: { title: 'Explainability', icon: '🔍', order: 6 },
  privacy: { title: 'Privacy', icon: '🔒', order: 7 },
  security: { title: 'Security', icon: '🔐', order: 8 },
  design: { title: 'Design & UX', icon: '🎨', order: 9 },
  reference_architectures: { title: 'Reference Architectures', icon: '🏛️', order: 10 },
}

export default function CatalogPage() {
  const router = useRouter()
  const [categories, setCategories] = useState<CategoriesMap>({})
  const [metadata, setMetadata] = useState<CatalogMetadata | null>(null)
  const [quickReference, setQuickReference] = useState<QuickReference | null>(null)
  const [resources, setResources] = useState<ResourcesData | null>(null)
  const [useCases, setUseCases] = useState<UseCasesData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedTools, setExpandedTools] = useState<Set<string>>(new Set())
  const [expandedUseCases, setExpandedUseCases] = useState<Set<string>>(new Set())
  const [activeTab, setActiveTab] = useState<'use-cases' | 'tools' | 'resources'>('use-cases')

  // Fetch tools and resources from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api'
        
        // Fetch tools and resources in parallel
        const [toolsResponse, refsResponse] = await Promise.all([
          fetch(apiUrl + '/tools'),
          fetch(apiUrl + '/references').catch(() => null) // Optional - don't fail if not available
        ])

        if (!toolsResponse.ok) {
          throw new Error('Failed to fetch tools: ' + toolsResponse.statusText)
        }

        const toolsData: ToolsApiResponse = await toolsResponse.json()
        setCategories(toolsData.tools || {})
        setMetadata(toolsData.metadata || null)
        setQuickReference(toolsData.quick_reference || null)
        setUseCases(toolsData.use_cases || null)
        
        // Set resources if available
        if (refsResponse && refsResponse.ok) {
          const refsData = await refsResponse.json()
          setResources(refsData.references || refsData || null)
        }
        
        setError(null)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError(err instanceof Error ? err.message : 'Failed to load tools catalog')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const scrollToCategory = useCallback((categoryId: string) => {
    const element = document.getElementById(categoryId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [])

  const toggleToolExpanded = useCallback((toolKey: string) => {
    setExpandedTools(prev => {
      const newSet = new Set(prev)
      if (newSet.has(toolKey)) {
        newSet.delete(toolKey)
      } else {
        newSet.add(toolKey)
      }
      return newSet
    })
  }, [])

  const toggleUseCaseExpanded = useCallback((useCaseId: string) => {
    setExpandedUseCases(prev => {
      const newSet = new Set(prev)
      if (newSet.has(useCaseId)) {
        newSet.delete(useCaseId)
      } else {
        newSet.add(useCaseId)
      }
      return newSet
    })
  }, [])

  // Get sorted categories based on config order
  const sortedCategoryIds = Object.keys(categories).sort((a, b) => {
    const orderA = categoryConfig[a]?.order || 100
    const orderB = categoryConfig[b]?.order || 100
    return orderA - orderB
  })

  // Render capability section (handles both array and object formats)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const renderCapabilities = (capabilities: ToolCapabilities | string[] | undefined | any) => {
    if (!capabilities) return null

    if (Array.isArray(capabilities)) {
      return (
        <ul>
          {capabilities.map((cap, idx) => (
            <li key={idx}>{typeof cap === 'string' ? cap : JSON.stringify(cap)}</li>
          ))}
        </ul>
      )
    }

    // Object format with sub-categories
    return (
      <div>
        {Object.entries(capabilities).map(([key, values]) => {
          // Handle different value types
          if (Array.isArray(values)) {
            // Array of strings
            return (
              <div key={key} style={{ marginBottom: '10px' }}>
                <strong style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}:</strong>
                <ul style={{ marginTop: '4px' }}>
                  {values.map((v, idx) => (
                    <li key={idx}>{typeof v === 'string' ? v : JSON.stringify(v)}</li>
                  ))}
                </ul>
              </div>
            )
          } else if (typeof values === 'object' && values !== null) {
            // Nested object (like attack_types: {evasion: "...", inference: "..."})
            return (
              <div key={key} style={{ marginBottom: '10px' }}>
                <strong style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}:</strong>
                <ul style={{ marginTop: '4px' }}>
                  {Object.entries(values).map(([subKey, subValue]) => (
                    <li key={subKey}>
                      <strong>{subKey.replace(/_/g, ' ')}:</strong> {String(subValue)}
                    </li>
                  ))}
                </ul>
              </div>
            )
          } else if (typeof values === 'string') {
            // Simple string value
            return (
              <div key={key} style={{ marginBottom: '10px' }}>
                <strong style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}:</strong> {values}
              </div>
            )
          }
          return null
        })}
      </div>
    )
  }

  // Generate tool key
  const getToolKey = (catId: string, toolName: string, idx: number) => {
    return catId + '-' + toolName + '-' + idx
  }

  return (
    <div className={styles.container}>
      {/* Pilot Banner */}
      <div className={styles.pilotBanner}>
        <span className={styles.pilotIcon}>🚀</span>
        <span>
          <strong>Pilot Phase:</strong> This RAI Tools Catalog features the latest Microsoft Ignite 2025 announcements.{' '}
          <a href="/submit">Submit your AI project</a> for a personalized review.
        </span>
      </div>

      {/* Header */}
      <header className={styles.header}>
        <button className={styles.backButton} onClick={() => router.push('/')}>
          ← Back to Home
        </button>
        <h1 className={styles.title}>Microsoft Responsible AI Tools Catalog</h1>
        <p className={styles.subtitle}>
          Comprehensive toolkit for building AI solutions that are fair, reliable, safe, private, inclusive, transparent, and accountable
        </p>
        {metadata?.last_updated && (
          <p style={{ fontSize: '14px', opacity: 0.8, marginTop: '10px' }}>
            Last Updated: {metadata.last_updated} {metadata.ignite_2025_updates && '• Includes Ignite 2025 Updates'}
          </p>
        )}
      </header>

      {/* Introduction */}
      <div className={styles.intro}>
        <p>
          This catalog provides a comprehensive overview of <strong>Microsoft Responsible AI tools and services</strong> to help you build AI solutions responsibly.
          Each tool is mapped to Microsoft&apos;s six core AI principles: Fairness, Reliability &amp; Safety, Privacy &amp; Security, Inclusiveness, Transparency, and Accountability.
        </p>
        <p>
          <strong>New for 2025:</strong> This catalog includes the latest announcements from Microsoft Ignite 2025, including the <strong>Foundry Control Plane</strong>,
          <strong> Agent 365</strong>, <strong>Foundry IQ</strong>, and other enterprise governance capabilities.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className={styles.tabContainer}>
        <button 
          className={`${styles.tab} ${activeTab === 'use-cases' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('use-cases')}
        >
          <span className={styles.tabIcon}>🎯</span>
          Use Cases
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'tools' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('tools')}
        >
          <span className={styles.tabIcon}>🛠️</span>
          Tools & Services
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'resources' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('resources')}
        >
          <span className={styles.tabIcon}>📚</span>
          Resources & Documentation
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
          <p style={{ fontSize: '18px', color: '#666' }}>Loading tools catalog...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div style={{ textAlign: 'center', padding: '60px 20px', background: '#fff3cd', margin: '20px', borderRadius: '12px' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚠️</div>
          <p style={{ fontSize: '18px', color: '#856404' }}>{error}</p>
          <button
            onClick={() => window.location.reload()}
            style={{ marginTop: '20px', padding: '10px 24px', background: '#0078d4', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Category Navigation - Tools Tab */}
      {!loading && !error && activeTab === 'tools' && sortedCategoryIds.length > 0 && (
        <nav className={styles.categoryNav}>
          <h3>Quick Navigation</h3>
          <div className={styles.categoryButtons}>
            {sortedCategoryIds.map(catId => {
              const config = categoryConfig[catId] || { title: catId.replace(/_/g, ' '), icon: '📦', order: 99 }
              const category = categories[catId]
              const toolCount = category?.tools?.length || 0

              return (
                <button
                  key={catId}
                  className={styles.categoryButton}
                  onClick={() => scrollToCategory(catId)}
                >
                  <span className={styles.catIcon}>{config.icon}</span>
                  <span className={styles.catLabel}>{config.title} ({toolCount})</span>
                </button>
              )
            })}
          </div>
        </nav>
      )}

      {/* Main Content - Use Cases Tab */}
      {activeTab === 'use-cases' && !loading && !error && (
        <main className={styles.main}>
          <section className={styles.categorySection}>
            <div className={styles.categoryHeader}>
              <span className={styles.categoryIcon}>🎯</span>
              <div>
                <h2 className={styles.categoryTitle}>Real-World Use Cases</h2>
                <p className={styles.categoryDescription}>
                  Step-by-step guidance for implementing Responsible AI in common scenarios. Each use case includes required tools, implementation steps, and success metrics.
                </p>
              </div>
            </div>

            {useCases?.scenarios && useCases.scenarios.length > 0 ? (
              <div className={styles.toolsGrid}>
                {useCases.scenarios.map((useCase) => {
                  const isExpanded = expandedUseCases.has(useCase.id)
                  
                  return (
                    <div
                      key={useCase.id}
                      className={`${styles.toolCard} ${isExpanded ? styles.expanded : ''}`}
                      style={{ gridColumn: isExpanded ? '1 / -1' : undefined }}
                    >
                      <div className={styles.toolHeader} onClick={() => toggleUseCaseExpanded(useCase.id)}>
                        <div>
                          <h3 className={styles.toolName}>{useCase.title}</h3>
                          <span style={{
                            display: 'inline-block',
                            background: useCase.risk_profile.includes('Critical') ? '#dc3545' : 
                                        useCase.risk_profile.includes('Very High') ? '#fd7e14' :
                                        useCase.risk_profile.includes('High') ? '#ffc107' : '#28a745',
                            color: useCase.risk_profile.includes('High') || useCase.risk_profile.includes('Critical') ? 'white' : 'black',
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '11px',
                            fontWeight: 600,
                            marginTop: '4px'
                          }}>
                            {useCase.risk_profile.split(' - ')[0]}
                          </span>
                        </div>
                        <span className={styles.expandIcon}>{isExpanded ? '−' : '+'}</span>
                      </div>

                      <p className={styles.toolDescription}>{useCase.description}</p>

                      {!isExpanded && (
                        <div style={{ marginTop: '12px' }}>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                            {useCase.industry_relevance?.slice(0, 3).map((industry, i) => (
                              <span key={i} className={styles.principleBadge} style={{ fontSize: '11px' }}>{industry}</span>
                            ))}
                            {(useCase.industry_relevance?.length || 0) > 3 && (
                              <span className={styles.principleBadge} style={{ fontSize: '11px' }}>+{useCase.industry_relevance.length - 3} more</span>
                            )}
                          </div>
                        </div>
                      )}

                      {isExpanded && (
                        <div className={styles.toolDetails}>
                          <div className={styles.detailSection}>
                            <h4>Industries</h4>
                            <div className={styles.principles}>
                              {useCase.industry_relevance?.map((industry, i) => (
                                <span key={i} className={styles.principleBadge}>{industry}</span>
                              ))}
                            </div>
                          </div>

                          <div className={styles.detailSection}>
                            <h4>⚠️ Risk Profile</h4>
                            <p>{useCase.risk_profile}</p>
                          </div>

                          {useCase.required_tools && useCase.required_tools.length > 0 && (
                          <div className={styles.detailSection}>
                            <h4>🔧 Required Tools</h4>
                            {useCase.required_tools.map((tool, i) => (
                              <div key={i} style={{ marginBottom: '12px', padding: '10px', background: '#f0f9ff', borderRadius: '8px', borderLeft: '3px solid #0078d4' }}>
                                <strong style={{ color: '#0078d4' }}>{tool.tool}</strong>
                                <p style={{ margin: '4px 0 0', fontSize: '13px' }}>{tool.purpose}</p>
                                {tool.configuration && (
                                  <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#666', fontStyle: 'italic' }}>
                                    Config: {tool.configuration}
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                          )}

                          {useCase.recommended_tools && useCase.recommended_tools.length > 0 && (
                            <div className={styles.detailSection}>
                              <h4>💡 Recommended Tools</h4>
                              {useCase.recommended_tools.map((tool, i) => (
                                <div key={i} style={{ marginBottom: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '6px' }}>
                                  <strong>{tool.tool}</strong>
                                  <span style={{ fontSize: '13px', color: '#666' }}> — {tool.purpose}</span>
                                </div>
                              ))}
                            </div>
                          )}

                          {useCase.implementation_steps && useCase.implementation_steps.length > 0 && (
                          <div className={styles.detailSection}>
                            <h4>📋 Implementation Steps</h4>
                            <ol style={{ paddingLeft: '20px', margin: 0 }}>
                              {useCase.implementation_steps.map((step, i) => (
                                <li key={i} style={{ marginBottom: '6px', fontSize: '14px' }}>{String(step).replace(/^\d+\.\s*/, '')}</li>
                              ))}
                            </ol>
                          </div>
                          )}

                          {useCase.success_metrics && useCase.success_metrics.length > 0 && (
                          <div className={styles.detailSection}>
                            <h4>✅ Success Metrics</h4>
                            <ul style={{ paddingLeft: '20px', margin: 0 }}>
                              {useCase.success_metrics.map((metric, i) => (
                                <li key={i} style={{ marginBottom: '4px', fontSize: '14px', color: '#28a745' }}>{metric}</li>
                              ))}
                            </ul>
                          </div>
                          )}

                          {useCase.common_pitfalls && useCase.common_pitfalls.length > 0 && (
                          <div className={styles.detailSection}>
                            <h4>⚠️ Common Pitfalls to Avoid</h4>
                            <ul style={{ paddingLeft: '20px', margin: 0 }}>
                              {useCase.common_pitfalls.map((pitfall, i) => (
                                <li key={i} style={{ marginBottom: '4px', fontSize: '14px', color: '#dc3545' }}>{pitfall}</li>
                              ))}
                            </ul>
                          </div>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                <p>Use cases are loading from the API...</p>
              </div>
            )}
          </section>

          {/* Quick Start Section */}
          <section className={styles.categorySection}>
            <div className={styles.categoryHeader}>
              <span className={styles.categoryIcon}>⚡</span>
              <div>
                <h2 className={styles.categoryTitle}>Quick Start: What&apos;s Your Top Concern?</h2>
                <p className={styles.categoryDescription}>
                  Jump straight to solutions based on your immediate needs
                </p>
              </div>
            </div>

            <div className={styles.toolsGrid}>
              {[
                { concern: 'My AI might generate harmful content', solution: 'Azure AI Content Safety', action: 'Enable all harm categories at severity threshold 2' },
                { concern: 'Users might try to jailbreak my AI', solution: 'Prompt Shields + PyRIT', action: 'Enable Prompt Shields on all user inputs' },
                { concern: 'My AI makes up information', solution: 'Groundedness Detection', action: 'Set threshold to 4+ for production' },
                { concern: 'My AI might be biased', solution: 'Fairlearn', action: 'Run MetricFrame analysis across protected groups' },
                { concern: 'I can\'t explain my AI\'s decisions', solution: 'InterpretML EBM', action: 'Train with Explainable Boosting Machine' },
                { concern: 'Data privacy and PII exposure', solution: 'Presidio', action: 'Implement PII detection in all data pipelines' },
              ].map((item, i) => (
                <div key={i} className={styles.toolCard}>
                  <h3 className={styles.toolName} style={{ fontSize: '14px', color: '#333' }}>&ldquo;{item.concern}&rdquo;</h3>
                  <p style={{ margin: '8px 0', fontWeight: 600, color: '#0078d4' }}>→ {item.solution}</p>
                  <p className={styles.toolDescription} style={{ fontSize: '13px' }}>{item.action}</p>
                </div>
              ))}
            </div>
          </section>
        </main>
      )}

      {/* Main Content - Tools Tab */}
      {activeTab === 'tools' && (
      <main className={styles.main}>
        {!loading && !error && sortedCategoryIds.map(catId => {
          const config = categoryConfig[catId] || { title: catId.replace(/_/g, ' '), icon: '📦', order: 99 }
          const category = categories[catId]
          const tools = category?.tools || []

          return (
            <section key={catId} id={catId} className={styles.categorySection}>
              <div className={styles.categoryHeader}>
                <span className={styles.categoryIcon}>{config.icon}</span>
                <div>
                  <h2 className={styles.categoryTitle}>{config.title}</h2>
                  <p className={styles.categoryDescription}>{category?.description || ''}</p>
                </div>
              </div>

              <div className={styles.toolsGrid}>
                {tools.map((tool, idx) => {
                  const toolKey = getToolKey(catId, tool.name, idx)
                  const isExpanded = expandedTools.has(toolKey)
                  const isIgnite2025 = tool.announced?.includes('Ignite 2025') || tool.status?.includes('Preview')
                  const docUrl = tool.documentation_url || tool.github_url || tool.url

                  return (
                    <div
                      key={toolKey}
                      className={styles.toolCard + (isExpanded ? ' ' + styles.expanded : '')}
                    >
                      <div className={styles.toolHeader} onClick={() => toggleToolExpanded(toolKey)}>
                        <div>
                          <h3 className={styles.toolName}>{tool.name}</h3>
                          {isIgnite2025 && (
                            <span style={{
                              display: 'inline-block',
                              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                              color: 'white',
                              padding: '2px 8px',
                              borderRadius: '12px',
                              fontSize: '11px',
                              fontWeight: 600,
                              marginTop: '4px'
                            }}>
                              ✨ {tool.status || 'Ignite 2025'}
                            </span>
                          )}
                        </div>
                        <span className={styles.expandIcon}>{isExpanded ? '−' : '+'}</span>
                      </div>

                      <p className={styles.toolDescription}>{tool.description}</p>

                      {isExpanded && (
                        <div className={styles.toolDetails}>
                          {tool.type && (
                            <div className={styles.detailSection}>
                              <h4>Type</h4>
                              <p style={{ textTransform: 'capitalize' }}>{tool.type}</p>
                            </div>
                          )}

                          {tool.capabilities && (
                            <div className={styles.detailSection}>
                              <h4>Capabilities</h4>
                              {renderCapabilities(tool.capabilities)}
                            </div>
                          )}

                          {tool.use_cases && tool.use_cases.length > 0 && (
                            <div className={styles.detailSection}>
                              <h4>Use Cases</h4>
                              <ul>
                                {tool.use_cases.map((uc, i) => (
                                  <li key={i}>{uc}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {tool.integration_points && tool.integration_points.length > 0 && (
                            <div className={styles.detailSection}>
                              <h4>Integration Points</h4>
                              <div className={styles.principles}>
                                {tool.integration_points.map((ip, i) => (
                                  <span key={i} className={styles.principleBadge}>{ip}</span>
                                ))}
                              </div>
                            </div>
                          )}

                          {tool.install && (
                            <div className={styles.detailSection}>
                              <h4>Installation</h4>
                              <code style={{
                                display: 'block',
                                background: '#f5f5f5',
                                padding: '8px 12px',
                                borderRadius: '4px',
                                fontSize: '13px',
                                overflowX: 'auto'
                              }}>
                                {tool.install}
                              </code>
                            </div>
                          )}

                          {docUrl && (
                            <a
                              href={docUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className={styles.toolLink}
                            >
                              View Documentation →
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </section>
          )
        })}

        {/* Quick Reference Section */}
        {!loading && !error && quickReference?.tool_by_risk && (
          <section className={styles.categorySection}>
            <div className={styles.categoryHeader}>
              <span className={styles.categoryIcon}>⚡</span>
              <div>
                <h2 className={styles.categoryTitle}>Quick Reference: Tools by Risk Type</h2>
                <p className={styles.categoryDescription}>
                  Find the right tools based on the specific risks you need to address
                </p>
              </div>
            </div>

            <div className={styles.toolsGrid}>
              {Object.entries(quickReference.tool_by_risk).map(([risk, data]) => {
                // Handle both old format (string[]) and new format (object with tools, first_action, documentation)
                const isNewFormat = data && typeof data === 'object' && !Array.isArray(data) && 'tools' in data
                const tools = isNewFormat ? (data as QuickReferenceItem).tools : (Array.isArray(data) ? data : [])
                const firstAction = isNewFormat ? (data as QuickReferenceItem).first_action : null
                
                return (
                  <div key={risk} className={styles.toolCard}>
                    <h3 className={styles.toolName} style={{ textTransform: 'capitalize' }}>
                      {risk.replace(/_/g, ' ')}
                    </h3>
                    <p className={styles.toolDescription}>
                      <strong>Tools:</strong> {tools.join(', ')}
                    </p>
                    {firstAction && (
                      <p style={{ fontSize: '13px', color: '#0078d4', marginTop: '8px' }}>
                        <strong>First Action:</strong> {firstAction}
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          </section>
        )}
      </main>
      )}

      {/* Resources & Documentation Tab */}
      {activeTab === 'resources' && !loading && !error && (
        <main className={styles.main}>
          {/* Resources Introduction */}
          <section className={styles.categorySection}>
            <div className={styles.categoryHeader}>
              <span className={styles.categoryIcon}>📖</span>
              <div>
                <h2 className={styles.categoryTitle}>Official Documentation & Resources</h2>
                <p className={styles.categoryDescription}>
                  Curated collection of Microsoft&apos;s Responsible AI documentation, guides, and reference architectures
                </p>
              </div>
            </div>
          </section>

          {/* Core Documentation */}
          {resources?.core_documentation && (
            <section className={styles.categorySection}>
              <div className={styles.categoryHeader}>
                <span className={styles.categoryIcon}>📚</span>
                <div>
                  <h2 className={styles.categoryTitle}>Core Documentation</h2>
                  <p className={styles.categoryDescription}>Essential Microsoft Responsible AI resources</p>
                </div>
              </div>
              <div className={styles.toolsGrid}>
                {Object.entries(resources.core_documentation).map(([key, resource]) => {
                  // Skip if not a valid resource object
                  if (!resource || typeof resource !== 'object' || !('url' in resource)) {
                    return null
                  }
                  return (
                    <a
                      key={key}
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.resourceCard}
                    >
                      <h3 className={styles.resourceTitle}>{resource.title}</h3>
                      <p className={styles.resourceDescription}>{resource.description}</p>
                      <span className={styles.resourceLink}>View Documentation →</span>
                    </a>
                  )
                })}
              </div>
            </section>
          )}

          {/* Microsoft Foundry */}
          {resources?.microsoft_foundry && (
            <section className={styles.categorySection}>
              <div className={styles.categoryHeader}>
                <span className={styles.categoryIcon}>🏗️</span>
                <div>
                  <h2 className={styles.categoryTitle}>Microsoft Foundry</h2>
                  <p className={styles.categoryDescription}>
                    {resources.microsoft_foundry.note || 'AI development platform (formerly Azure AI Foundry)'}
                  </p>
                </div>
              </div>
              <div className={styles.toolsGrid}>
                {Object.entries(resources.microsoft_foundry)
                  .filter(([key]) => key !== 'note')
                  .map(([key, resource]) => {
                    if (typeof resource === 'string') return null
                    const res = resource as ResourceLink
                    return (
                      <a
                        key={key}
                        href={res.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.resourceCard}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <h3 className={styles.resourceTitle}>{res.title}</h3>
                          {res.status && (
                            <span className={styles.previewBadge}>{res.status}</span>
                          )}
                        </div>
                        <p className={styles.resourceDescription}>{res.description}</p>
                        <span className={styles.resourceLink}>View Documentation →</span>
                      </a>
                    )
                  })}
              </div>
            </section>
          )}

          {/* Other Resource Categories */}
          {(['content_safety', 'evaluation', 'fairness', 'explainability', 'privacy', 'security', 'design', 'reference_architectures'] as const).map(categoryKey => {
            const category = resources?.[categoryKey]
            if (!category) return null
            const config = resourceCategoryConfig[categoryKey] || { title: categoryKey, icon: '📦', order: 99 }
            
            return (
              <section key={categoryKey} className={styles.categorySection}>
                <div className={styles.categoryHeader}>
                  <span className={styles.categoryIcon}>{config.icon}</span>
                  <div>
                    <h2 className={styles.categoryTitle}>{config.title}</h2>
                  </div>
                </div>
                <div className={styles.toolsGrid}>
                  {Object.entries(category).map(([key, resource]) => {
                    // Skip if not a valid resource object
                    if (!resource || typeof resource !== 'object' || !('url' in resource)) {
                      return null
                    }
                    const res = resource as ResourceLink
                    return (
                      <a
                        key={key}
                        href={res.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.resourceCard}
                      >
                        <h3 className={styles.resourceTitle}>{res.title}</h3>
                        <p className={styles.resourceDescription}>{res.description}</p>
                        <span className={styles.resourceLink}>
                          {res.url?.includes('github.com') ? 'View on GitHub →' : 'View Documentation →'}
                        </span>
                      </a>
                    )
                  })}
                </div>
              </section>
            )
          })}

          {/* Fallback if no resources loaded */}
          {!resources && (
            <section className={styles.categorySection}>
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <p style={{ fontSize: '16px', color: '#666' }}>
                  Resources are being loaded from the API. If this persists, please check the backend connection.
                </p>
              </div>
            </section>
          )}
        </main>
      )}

      {/* Footer */}
      <footer className={styles.footer}>
        <p>
          Part of the <strong>Responsible AI Agent</strong> pilot program.{' '}
          <a href="https://www.microsoft.com/ai/responsible-ai" target="_blank" rel="noopener noreferrer">
            Learn more about Microsoft Responsible AI
          </a>
        </p>
        <p style={{ marginTop: '10px', fontSize: '13px' }}>
          {metadata?.version && ('Catalog Version: ' + metadata.version + ' • ')}
          Data sourced from Microsoft official documentation and Ignite 2025 announcements.
        </p>
      </footer>
    </div>
  )
}
