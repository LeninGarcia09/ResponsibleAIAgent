'use client'

import { useRouter } from 'next/navigation'
import Footer from '../components/Footer'
import FeedbackButton from '../components/FeedbackButton'
import styles from './page.module.css'

// Example use cases for users who don't know where to start
const USE_CASE_EXAMPLES = [
  {
    icon: '💬',
    title: 'Customer Service Chatbot',
    stage: 'Just an idea',
    description: 'I want to build a chatbot to answer customer questions about our products.',
    prompt: 'We\'re thinking about building a customer service chatbot using AI to help answer common questions. We sell consumer electronics. Not sure where to start with responsible AI.'
  },
  {
    icon: '📄',
    title: 'Document Summarization',
    stage: 'Early planning',
    description: 'Summarize long reports and contracts for our legal team.',
    prompt: 'We need an AI tool that can summarize legal contracts and documents for our legal team. Documents may contain confidential client information.'
  },
  {
    icon: '👥',
    title: 'Resume Screening',
    stage: 'Considering options',
    description: 'Help HR team screen job applications more efficiently.',
    prompt: 'Our HR department wants to use AI to help screen resumes and identify qualified candidates. We\'re concerned about bias and fairness.'
  },
  {
    icon: '🏥',
    title: 'Healthcare Assistant',
    stage: 'Research phase',
    description: 'AI assistant to help patients find information about symptoms.',
    prompt: 'We\'re a healthcare provider exploring an AI chatbot to help patients find information about symptoms and book appointments. Need to understand HIPAA implications.'
  },
  {
    icon: '📊',
    title: 'Sales Forecasting',
    stage: 'Planning',
    description: 'Predict sales trends and inventory needs.',
    prompt: 'We want to use AI to predict sales trends and optimize inventory. The system would analyze historical sales data and market trends.'
  },
  {
    icon: '🎓',
    title: 'Educational Tutor',
    stage: 'Concept phase',
    description: 'AI tutor to help students learn at their own pace.',
    prompt: 'We\'re an EdTech company thinking about an AI tutor for K-12 students. It would help with homework and explain concepts. Concerned about safety for children.'
  }
]

// FAQ items for users with basic questions
const FAQ_ITEMS = [
  {
    question: 'I only have a rough idea - can I still use this?',
    answer: 'Absolutely! Our AI agent is designed to help at any stage. Even if you just have a concept like "I want to use AI to help customers," we can provide guidance on what to consider, potential risks, and recommended approaches.'
  },
  {
    question: 'What information do I need to provide?',
    answer: 'At minimum, just describe what you\'re trying to accomplish. The more details you provide about your industry, users, and data, the more specific our recommendations will be. But even a one-sentence description works!'
  },
  {
    question: 'How long does a review take?',
    answer: 'Reviews are AI-powered and typically complete in under a minute. You\'ll receive immediate feedback with actionable recommendations.'
  },
  {
    question: 'What will I get from this review?',
    answer: 'You\'ll receive: a risk assessment score, relevant compliance frameworks (like GDPR, HIPAA), specific recommendations for your use case, suggested Azure tools and services, and reference architectures you can follow.'
  },
  {
    question: 'Is my information kept confidential?',
    answer: 'Yes. This is an internal Microsoft tool and your submissions are treated as confidential. We don\'t share your project details externally.'
  }
]

// Stages of AI development with guidance
const DEVELOPMENT_STAGES = [
  {
    icon: '💡',
    stage: 'Just an Idea',
    color: '#0078d4',
    description: 'You have a concept but haven\'t started planning',
    whatWeHelp: [
      'Identify potential risks early',
      'Understand applicable regulations',
      'Get reference architectures to follow',
      'Learn about required safeguards'
    ]
  },
  {
    icon: '📋',
    stage: 'Planning Phase',
    color: '#00a4ef',
    description: 'You\'re researching options and approaches',
    whatWeHelp: [
      'Compare responsible AI approaches',
      'Identify required Azure services',
      'Plan for data privacy requirements',
      'Design human oversight mechanisms'
    ]
  },
  {
    icon: '🔧',
    stage: 'Development',
    color: '#7fba00',
    description: 'You\'re actively building your solution',
    whatWeHelp: [
      'Review implementation for best practices',
      'Suggest specific tools and SDKs',
      'Provide code patterns for safety',
      'Identify testing requirements'
    ]
  },
  {
    icon: '🚀',
    stage: 'Production',
    color: '#f25022',
    description: 'Your solution is live or about to launch',
    whatWeHelp: [
      'Audit current implementation',
      'Identify gaps before incidents occur',
      'Recommend monitoring solutions',
      'Ensure compliance documentation'
    ]
  }
]

export default function Home() {
  const router = useRouter()

  const handleExampleClick = (prompt: string) => {
    // Store the example prompt in sessionStorage to pre-fill the form
    sessionStorage.setItem('examplePrompt', prompt)
    router.push('/submit')
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
        <div className={styles.headerContent}>
          <h1 className={styles.title}>🤖 Responsible AI Agent</h1>
          <p className={styles.subtitle}>
            Get AI-powered guidance on responsible AI practices — at any stage of your project
          </p>
        </div>
      </header>

      <main className={styles.main}>
        {/* Hero Section */}
        <div className={styles.hero}>
          <h2 className={styles.heroTitle}>
            Not sure where to start? That's exactly why we're here.
          </h2>
          <p className={styles.heroDescription}>
            Whether you have a detailed specification or just a rough idea, our AI agent helps you 
            understand responsible AI requirements, identify risks, and get actionable recommendations.
            <strong> No expertise required.</strong>
          </p>

          <div className={styles.heroButtons}>
            <button 
              className={styles.btnPrimary} 
              onClick={() => router.push('/submit')}
            >
              🚀 Start My Review
            </button>
            <button 
              className={styles.btnSecondary} 
              onClick={() => router.push('/reviews')}
            >
              📋 View Past Reviews
            </button>
            <button 
              className={styles.btnOutline} 
              onClick={() => router.push('/catalog')}
            >
              📚 RAI Tools Catalog
            </button>
          </div>
        </div>

        {/* What Stage Are You At? */}
        <section className={styles.stagesSection}>
          <h2 className={styles.sectionTitle}>📍 What stage is your AI project?</h2>
          <p className={styles.sectionSubtitle}>
            We provide tailored guidance no matter where you are in your journey
          </p>
          
          <div className={styles.stagesGrid}>
            {DEVELOPMENT_STAGES.map((stage, index) => (
              <div 
                key={index} 
                className={styles.stageCard}
                style={{ borderTopColor: stage.color }}
              >
                <div className={styles.stageHeader}>
                  <span className={styles.stageIcon}>{stage.icon}</span>
                  <h3 className={styles.stageTitle}>{stage.stage}</h3>
                </div>
                <p className={styles.stageDescription}>{stage.description}</p>
                <div className={styles.stageHelp}>
                  <strong>We help you:</strong>
                  <ul>
                    {stage.whatWeHelp.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Example Use Cases */}
        <section className={styles.examplesSection}>
          <h2 className={styles.sectionTitle}>💡 Example Submissions</h2>
          <p className={styles.sectionSubtitle}>
            Click any example to see how easy it is to get started — even with minimal details
          </p>
          
          <div className={styles.examplesGrid}>
            {USE_CASE_EXAMPLES.map((example, index) => (
              <button
                key={index}
                className={styles.exampleCard}
                onClick={() => handleExampleClick(example.prompt)}
              >
                <div className={styles.exampleHeader}>
                  <span className={styles.exampleIcon}>{example.icon}</span>
                  <span className={styles.exampleStage}>{example.stage}</span>
                </div>
                <h3 className={styles.exampleTitle}>{example.title}</h3>
                <p className={styles.exampleDescription}>{example.description}</p>
                <div className={styles.examplePrompt}>
                  <strong>Sample input:</strong>
                  <q>{example.prompt}</q>
                </div>
                <span className={styles.exampleCta}>Try this example →</span>
              </button>
            ))}
          </div>
        </section>

        {/* What You'll Get */}
        <section className={styles.benefitsSection}>
          <h2 className={styles.sectionTitle}>📊 What You'll Receive</h2>
          <p className={styles.sectionSubtitle}>
            Every review provides comprehensive, actionable insights
          </p>
          
          <div className={styles.benefitsGrid}>
            <div className={styles.benefitCard}>
              <div className={styles.benefitIcon}>🎯</div>
              <h3>Risk Score</h3>
              <p>A 0-100 risk assessment with breakdown by category (privacy, bias, safety, etc.)</p>
            </div>
            <div className={styles.benefitCard}>
              <div className={styles.benefitIcon}>⚖️</div>
              <h3>Compliance Guidance</h3>
              <p>Relevant frameworks like EU AI Act, GDPR, HIPAA with specific requirements</p>
            </div>
            <div className={styles.benefitCard}>
              <div className={styles.benefitIcon}>📐</div>
              <h3>Reference Architectures</h3>
              <p>Pre-built solution patterns with Azure services and implementation steps</p>
            </div>
            <div className={styles.benefitCard}>
              <div className={styles.benefitIcon}>🛠️</div>
              <h3>Tool Recommendations</h3>
              <p>Specific Azure AI services, SDKs, and open-source tools for your use case</p>
            </div>
            <div className={styles.benefitCard}>
              <div className={styles.benefitIcon}>✅</div>
              <h3>Action Checklist</h3>
              <p>Prioritized list of what to implement, from critical to nice-to-have</p>
            </div>
            <div className={styles.benefitCard}>
              <div className={styles.benefitIcon}>💻</div>
              <h3>Code Examples</h3>
              <p>Ready-to-use code snippets for content filtering, logging, and safety measures</p>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className={styles.faqSection}>
          <h2 className={styles.sectionTitle}>❓ Frequently Asked Questions</h2>
          
          <div className={styles.faqGrid}>
            {FAQ_ITEMS.map((faq, index) => (
              <div key={index} className={styles.faqCard}>
                <h3 className={styles.faqQuestion}>{faq.question}</h3>
                <p className={styles.faqAnswer}>{faq.answer}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <div className={styles.cta}>
          <h2 className={styles.ctaTitle}>
            Ready to get started?
          </h2>
          <p className={styles.ctaDescription}>
            Just describe your AI idea — even a single sentence works. 
            Our agent will guide you from there.
          </p>
          <div className={styles.ctaButtons}>
            <button 
              className={styles.btnCtaPrimary} 
              onClick={() => router.push('/submit')}
            >
              🚀 Start My Review
            </button>
            <div className={styles.ctaHint}>
              Takes less than 2 minutes • No technical expertise required
            </div>
          </div>
        </div>
      </main>

      <Footer />
      <FeedbackButton context="home" />
    </div>
  )
}


