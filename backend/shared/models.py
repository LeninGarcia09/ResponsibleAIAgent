"""
Data models for the Responsible AI Agent.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    """Status of an AI review."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResponsibleAIPrinciple(str, Enum):
    """Microsoft Responsible AI Principles."""
    FAIRNESS = "fairness"
    INCLUSIVENESS = "inclusiveness"
    RELIABILITY = "reliability"
    SAFETY = "safety"
    TRANSPARENCY = "transparency"
    PRIVACY = "privacy"
    ACCOUNTABILITY = "accountability"


class SecurityCheckType(str, Enum):
    """Types of security checks."""
    DATA_ENCRYPTION = "data_encryption"
    ACCESS_CONTROL = "access_control"
    AUTHENTICATION = "authentication"
    COMPLIANCE = "compliance"
    SECURE_DEPLOYMENT = "secure_deployment"
    DATA_GOVERNANCE = "data_governance"


class SeverityLevel(str, Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    """A finding from the AI review."""
    principle: str
    severity: SeverityLevel
    title: str
    description: str
    recommendation: str
    compliant: bool


class SecurityCheck(BaseModel):
    """Security check result."""
    check_type: SecurityCheckType
    passed: bool
    title: str
    description: str
    recommendation: Optional[str] = None


class AIReviewSubmission(BaseModel):
    """Submission for AI solution review."""
    id: Optional[str] = None
    submission_date: Optional[datetime] = None
    submitter_email: str
    submitter_name: str
    project_name: str
    project_description: str
    ai_capabilities: List[str]
    data_sources: List[str]
    user_impact: str
    deployment_stage: str
    
    # Responsible AI Questions
    fairness_assessment: Optional[str] = None
    bias_testing: Optional[str] = None
    transparency_measures: Optional[str] = None
    privacy_controls: Optional[str] = None
    accountability_framework: Optional[str] = None
    
    # Security Questions
    data_encryption_method: Optional[str] = None
    access_control_mechanism: Optional[str] = None
    compliance_certifications: List[str] = Field(default_factory=list)
    
    # Additional context
    additional_context: Optional[Dict[str, Any]] = None
    
    # Review metadata
    status: ReviewStatus = ReviewStatus.PENDING
    assigned_reviewer: Optional[str] = None


class ReviewResult(BaseModel):
    """Result of an AI review."""
    review_id: str
    submission_id: str
    review_date: datetime
    overall_score: float  # 0-100
    overall_status: str  # "Approved", "Approved with Conditions", "Rejected"
    
    # Findings
    responsible_ai_findings: List[Finding]
    security_findings: List[Finding]
    security_checks: List[SecurityCheck]
    
    # Summary
    executive_summary: str
    key_risks: List[str]
    recommendations: List[str]
    
    # Compliance
    compliant_principles: List[str]
    non_compliant_principles: List[str]
    
    # Report metadata
    report_url: Optional[str] = None
    report_html: Optional[str] = None
    generated_by: str = "Responsible AI Agent"
    reviewer_notes: Optional[str] = None


class EmailRequest(BaseModel):
    """Request to send an email notification."""
    to_emails: List[str]
    subject: str
    body_html: str
    attachments: Optional[List[Dict[str, str]]] = None
