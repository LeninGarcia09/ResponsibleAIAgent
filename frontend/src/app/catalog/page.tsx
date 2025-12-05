'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import styles from './catalog.module.css'

interface Tool {
  name: string
  description: string
  useCases: string[]
  projectPhase: string
  principles: string[]
  availability: string
  url?: string
}

interface Category {
  id: string
  title: string
  icon: string
  description: string
  tools: Tool[]
}

const categories: Category[] = [
  {
    id: 'fairness',
    title: 'Fairness & Bias Mitigation',
    icon: '⚖️',
    description: 'Tools and resources focused on identifying and mitigating biases in AI systems to ensure fairness in outcomes.',
    tools: [
      {
        name: 'Fairlearn',
        description: 'Python toolkit to assess and improve model fairness. Includes metrics and mitigation algorithms.',
        useCases: ['Detecting bias in hiring models', 'Testing fairness in lending algorithms'],
        projectPhase: 'Model evaluation',
        principles: ['Fairness'],
        availability: 'External',
        url: 'https://github.com/fairlearn/fairlearn'
      },
      {
        name: 'Responsible AI Dashboard',
        description: 'Integrated UI for fairness, explainability, and error analysis. Combines Fairlearn, InterpretML, and other tools.',
        useCases: ['Holistic model assessment', 'Bias and accuracy debugging'],
        projectPhase: 'Model evaluation',
        principles: ['Fairness', 'Transparency', 'Reliability'],
        availability: 'External',
        url: 'https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai-dashboard'
      }
    ]
  },
  {
    id: 'transparency',
    title: 'Transparency & Explainability',
    icon: '🔍',
    description: 'Tools and practices that improve transparency of AI systems, making model behavior and decisions understandable to stakeholders.',
    tools: [
      {
        name: 'InterpretML',
        description: 'Toolkit for model interpretability. Supports glass-box and black-box explanation techniques.',
        useCases: ['Explaining feature importance', 'Creating stakeholder reports'],
        projectPhase: 'Model development',
        principles: ['Transparency'],
        availability: 'External',
        url: 'https://github.com/interpretml/interpret'
      },
      {
        name: 'Human-AI Experience (HAX) Toolkit',
        description: 'Design toolkit for building human-centered AI systems. Includes guidelines, workbook, and playbook.',
        useCases: ['Designing intuitive AI interfaces', 'Planning for user feedback and error recovery'],
        projectPhase: 'Design',
        principles: ['Transparency', 'Inclusiveness'],
        availability: 'External',
        url: 'https://www.microsoft.com/en-us/haxtoolkit/'
      }
    ]
  },
  {
    id: 'reliability',
    title: 'Reliability & Safety',
    icon: '🛡️',
    description: 'Tools to ensure models are reliable (accurate and robust) and safe from failures or misuse. This covers testing models for errors, monitoring performance, and safeguarding against harmful outputs or attacks.',
    tools: [
      {
        name: 'Azure AI Content Safety',
        description: 'Service to detect and mitigate harmful content in text and images.',
        useCases: ['Moderating user-generated content', 'Filtering generative AI outputs'],
        projectPhase: 'Deployment',
        principles: ['Safety'],
        availability: 'External',
        url: 'https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview'
      },
      {
        name: 'Counterfit',
        description: 'Open-source tool for adversarial security testing of ML models.',
        useCases: ['Testing model robustness', 'Simulating adversarial attacks'],
        projectPhase: 'Security assessment',
        principles: ['Reliability & Safety'],
        availability: 'External',
        url: 'https://github.com/Azure/counterfit'
      },
      {
        name: 'PyRIT',
        description: 'Python Risk Identification Toolkit for red teaming generative AI systems.',
        useCases: ['Prompt injection testing', 'Failure mode discovery'],
        projectPhase: 'Security assessment',
        principles: ['Reliability & Safety'],
        availability: 'External',
        url: 'https://github.com/microsoft/PyRIT'
      }
    ]
  },
  {
    id: 'privacy',
    title: 'Privacy & Security',
    icon: '🔒',
    description: 'Tools and frameworks to protect privacy and ensure security of data and AI systems, aligning with the Privacy & Security principle.',
    tools: [
      {
        name: 'Presidio',
        description: 'Open-source SDK for detecting and anonymizing PII in text and images.',
        useCases: ['Anonymizing chat logs', 'Redacting sensitive image data'],
        projectPhase: 'Data preparation',
        principles: ['Privacy & Security'],
        availability: 'External',
        url: 'https://github.com/microsoft/presidio'
      }
    ]
  },
  {
    id: 'inclusiveness',
    title: 'Inclusiveness & Accessibility',
    icon: '🌍',
    description: 'Resources that help make AI systems inclusive and accessible, ensuring they empower people of diverse backgrounds and abilities.',
    tools: [
      {
        name: 'Human-AI Experience (HAX) Toolkit',
        description: 'Design toolkit for building human-centered AI systems. Includes guidelines, workbook, and playbook. Also supports inclusiveness through accommodating diverse user needs.',
        useCases: ['Designing intuitive AI interfaces', 'Planning for user feedback and error recovery'],
        projectPhase: 'Design',
        principles: ['Transparency', 'Inclusiveness'],
        availability: 'External',
        url: 'https://www.microsoft.com/en-us/haxtoolkit/'
      }
    ]
  },
  {
    id: 'accountability',
    title: 'Accountability & Governance',
    icon: '📋',
    description: 'Governance frameworks and tools that drive accountability in AI development – ensuring people are responsible for AI outcomes and AI systems comply with ethical and legal requirements.',
    tools: [
      {
        name: 'Microsoft Responsible AI Standard (RAIS)',
        description: 'Internal framework with 14 goals and requirements for responsible AI development.',
        useCases: ['Governance and compliance', 'Project planning and review'],
        projectPhase: 'All phases',
        principles: ['All principles'],
        availability: 'Internal',
        url: 'https://blogs.microsoft.com/on-the-issues/2022/06/21/microsofts-framework-for-building-ai-systems-responsibly/'
      }
    ]
  }
]

export default function CatalogPage() {
  const router = useRouter()
  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const [expandedTools, setExpandedTools] = useState<Set<string>>(new Set())

  const toggleTool = (toolName: string) => {
    const newExpanded = new Set(expandedTools)
    if (newExpanded.has(toolName)) {
      newExpanded.delete(toolName)
    } else {
      newExpanded.add(toolName)
    }
    setExpandedTools(newExpanded)
  }

  const scrollToCategory = (categoryId: string) => {
    setActiveCategory(categoryId)
    const element = document.getElementById(categoryId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

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
        <button onClick={() => router.push('/')} className={styles.backButton}>
          ← Back to Home
        </button>
        <h1 className={styles.title}>📚 Microsoft Responsible AI Tools & Resources</h1>
        <p className={styles.subtitle}>
          Comprehensive catalog of tools, frameworks, and practices to uphold Microsoft&apos;s six AI principles
        </p>
      </header>

      <div className={styles.intro}>
        <p>
          Microsoft provides a robust ecosystem of Responsible AI (RAI) tools, frameworks, and practices to uphold its 
          <strong> six AI principles</strong> – fairness, reliability & safety, privacy & security, inclusiveness, 
          transparency, and accountability.
        </p>
        <p>
          Below is a comprehensive catalog of currently active, supported RAI tools and resources developed or integrated 
          by Microsoft, organized by area of focus (principle) and indicating the project phase when each is used, 
          typical use cases, the RAI principle(s) it supports, and whether it is for internal Microsoft use only or 
          available to external users.
        </p>
      </div>

      <nav className={styles.categoryNav}>
        <h3>Jump to Category:</h3>
        <div className={styles.categoryButtons}>
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => scrollToCategory(cat.id)}
              className={`${styles.categoryButton} ${activeCategory === cat.id ? styles.active : ''}`}
            >
              <span className={styles.catIcon}>{cat.icon}</span>
              <span className={styles.catLabel}>{cat.title}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className={styles.main}>
        {categories.map(category => (
          <section key={category.id} id={category.id} className={styles.categorySection}>
            <div className={styles.categoryHeader}>
              <span className={styles.categoryIcon}>{category.icon}</span>
              <div>
                <h2 className={styles.categoryTitle}>{category.title}</h2>
                <p className={styles.categoryDescription}>{category.description}</p>
              </div>
            </div>

            <div className={styles.toolsGrid}>
              {category.tools.map(tool => (
                <div 
                  key={tool.name} 
                  className={`${styles.toolCard} ${expandedTools.has(tool.name) ? styles.expanded : ''}`}
                >
                  <div 
                    className={styles.toolHeader}
                    onClick={() => toggleTool(tool.name)}
                  >
                    <h3 className={styles.toolName}>{tool.name}</h3>
                    <span className={styles.expandIcon}>
                      {expandedTools.has(tool.name) ? '−' : '+'}
                    </span>
                  </div>

                  <p className={styles.toolDescription}>{tool.description}</p>

                  {expandedTools.has(tool.name) && (
                    <div className={styles.toolDetails}>
                      <div className={styles.detailSection}>
                        <h4>Use Cases:</h4>
                        <ul>
                          {tool.useCases.map((uc, i) => (
                            <li key={i}>{uc}</li>
                          ))}
                        </ul>
                      </div>

                      <div className={styles.detailSection}>
                        <h4>Project Phase:</h4>
                        <p>{tool.projectPhase}</p>
                      </div>

                      <div className={styles.detailSection}>
                        <h4>RAI Principles:</h4>
                        <div className={styles.principles}>
                          {tool.principles.map(p => (
                            <span key={p} className={styles.principleBadge}>{p}</span>
                          ))}
                        </div>
                      </div>

                      <div className={styles.detailSection}>
                        <h4>Availability:</h4>
                        <p>{tool.availability}</p>
                      </div>
                    </div>
                  )}

                  {tool.url && (
                    <a 
                      href={tool.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className={styles.toolLink}
                    >
                      View Documentation ↗
                    </a>
                  )}
                </div>
              ))}
            </div>
          </section>
        ))}
      </main>

      <footer className={styles.footer}>
        <p>
          For more information, visit the{' '}
          <a href="https://www.microsoft.com/ai/responsible-ai" target="_blank" rel="noopener noreferrer">
            Microsoft Responsible AI homepage
          </a>
        </p>
      </footer>
    </div>
  )
}
