"""
Azure Function: Process AI Review
Triggered by Cosmos DB changes or HTTP request
"""
import azure.functions as func
import json
import logging
from datetime import datetime
from typing import List, Dict
from shared.models import (
    AIReviewSubmission,
    ReviewResult,
    Finding,
    SecurityCheck,
    SeverityLevel,
    SecurityCheckType,
    ResponsibleAIPrinciple
)
from shared.azure_clients import get_openai_client, get_cosmos_client
from shared.config import settings

logger = logging.getLogger(__name__)


class ResponsibleAIReviewEngine:
    """Core engine for reviewing AI solutions against Responsible AI principles."""
    
    def __init__(self):
        self.openai_client = get_openai_client()
    
    async def review_submission(self, submission: AIReviewSubmission) -> ReviewResult:
        """
        Perform comprehensive Responsible AI review.
        
        Args:
            submission: The AI solution submission to review
            
        Returns:
            ReviewResult with findings and recommendations
        """
        logger.info(f"Starting review for submission {submission.id}")
        
        # Perform individual assessments
        fairness_findings = await self._assess_fairness(submission)
        reliability_findings = await self._assess_reliability(submission)
        transparency_findings = await self._assess_transparency(submission)
        privacy_findings = await self._assess_privacy(submission)
        accountability_findings = await self._assess_accountability(submission)
        security_checks = await self._perform_security_checks(submission)
        
        # Combine all findings
        all_findings = (
            fairness_findings +
            reliability_findings +
            transparency_findings +
            privacy_findings +
            accountability_findings
        )
        
        # Calculate overall score
        overall_score = self._calculate_score(all_findings, security_checks)
        
        # Determine overall status
        overall_status = self._determine_status(overall_score, all_findings)
        
        # Generate executive summary
        executive_summary = await self._generate_executive_summary(
            submission, all_findings, security_checks, overall_score
        )
        
        # Extract key risks and recommendations
        key_risks = self._extract_key_risks(all_findings)
        recommendations = self._extract_recommendations(all_findings, security_checks)
        
        # Determine compliance
        compliant_principles = [f.principle for f in all_findings if f.compliant]
        non_compliant_principles = [f.principle for f in all_findings if not f.compliant]
        
        # Create review result
        review_result = ReviewResult(
            review_id=f"REV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            submission_id=submission.id,
            review_date=datetime.utcnow(),
            overall_score=overall_score,
            overall_status=overall_status,
            responsible_ai_findings=all_findings,
            security_findings=[],
            security_checks=security_checks,
            executive_summary=executive_summary,
            key_risks=key_risks,
            recommendations=recommendations,
            compliant_principles=list(set(compliant_principles)),
            non_compliant_principles=list(set(non_compliant_principles))
        )
        
        logger.info(f"Review completed for submission {submission.id}: {overall_status}")
        return review_result
    
    async def _assess_fairness(self, submission: AIReviewSubmission) -> List[Finding]:
        """Assess fairness and inclusiveness."""
        findings = []
        
        # Use Azure OpenAI to analyze fairness
        if self.openai_client:
            prompt = f"""
            Review the following AI solution for fairness and inclusiveness according to Microsoft's Responsible AI Standards:
            
            Project: {submission.project_name}
            Description: {submission.project_description}
            Fairness Assessment: {submission.fairness_assessment or 'Not provided'}
            Bias Testing: {submission.bias_testing or 'Not provided'}
            User Impact: {submission.user_impact}
            
            Analyze:
            1. Are there measures to identify and mitigate bias?
            2. Is the solution inclusive of diverse user groups?
            3. Are fairness metrics being tracked?
            4. Is there a process for handling fairness complaints?
            
            Provide findings in JSON format:
            {{
                "compliant": true/false,
                "severity": "critical/high/medium/low/info",
                "title": "Brief title",
                "description": "Detailed description",
                "recommendation": "Specific recommendation"
            }}
            """
            
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a Responsible AI expert reviewing AI solutions for compliance with Microsoft's Responsible AI Standards."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content)
                finding = Finding(
                    principle=ResponsibleAIPrinciple.FAIRNESS,
                    severity=SeverityLevel(result.get("severity", "info")),
                    title=result.get("title", "Fairness Assessment"),
                    description=result.get("description", ""),
                    recommendation=result.get("recommendation", ""),
                    compliant=result.get("compliant", False)
                )
                findings.append(finding)
            except Exception as e:
                logger.error(f"Error assessing fairness: {str(e)}")
                # Fallback finding
                findings.append(Finding(
                    principle=ResponsibleAIPrinciple.FAIRNESS,
                    severity=SeverityLevel.MEDIUM,
                    title="Fairness Assessment Required",
                    description="Unable to automatically assess fairness. Manual review required.",
                    recommendation="Conduct thorough bias testing and fairness evaluation.",
                    compliant=False
                ))
        
        return findings
    
    async def _assess_reliability(self, submission: AIReviewSubmission) -> List[Finding]:
        """Assess reliability and safety."""
        findings = []
        
        if not submission.ai_capabilities:
            findings.append(Finding(
                principle=ResponsibleAIPrinciple.RELIABILITY,
                severity=SeverityLevel.HIGH,
                title="AI Capabilities Not Specified",
                description="The AI capabilities are not clearly defined.",
                recommendation="Provide detailed information about AI capabilities and their reliability measures.",
                compliant=False
            ))
        
        return findings
    
    async def _assess_transparency(self, submission: AIReviewSubmission) -> List[Finding]:
        """Assess transparency measures."""
        findings = []
        
        if not submission.transparency_measures:
            findings.append(Finding(
                principle=ResponsibleAIPrinciple.TRANSPARENCY,
                severity=SeverityLevel.MEDIUM,
                title="Transparency Measures Not Documented",
                description="No transparency measures documented for the AI solution.",
                recommendation="Document how the AI system's decisions are explained to users.",
                compliant=False
            ))
        else:
            findings.append(Finding(
                principle=ResponsibleAIPrinciple.TRANSPARENCY,
                severity=SeverityLevel.INFO,
                title="Transparency Measures Documented",
                description=f"Transparency measures: {submission.transparency_measures}",
                recommendation="Continue maintaining transparent communication about AI capabilities and limitations.",
                compliant=True
            ))
        
        return findings
    
    async def _assess_privacy(self, submission: AIReviewSubmission) -> List[Finding]:
        """Assess privacy and security controls."""
        findings = []
        
        if not submission.privacy_controls:
            findings.append(Finding(
                principle=ResponsibleAIPrinciple.PRIVACY,
                severity=SeverityLevel.CRITICAL,
                title="Privacy Controls Not Specified",
                description="No privacy controls documented.",
                recommendation="Implement and document privacy controls including data minimization, consent management, and data retention policies.",
                compliant=False
            ))
        
        return findings
    
    async def _assess_accountability(self, submission: AIReviewSubmission) -> List[Finding]:
        """Assess accountability framework."""
        findings = []
        
        if not submission.accountability_framework:
            findings.append(Finding(
                principle=ResponsibleAIPrinciple.ACCOUNTABILITY,
                severity=SeverityLevel.HIGH,
                title="Accountability Framework Missing",
                description="No accountability framework documented.",
                recommendation="Establish clear accountability including ownership, governance, and incident response procedures.",
                compliant=False
            ))
        
        return findings
    
    async def _perform_security_checks(self, submission: AIReviewSubmission) -> List[SecurityCheck]:
        """Perform security best practices checks."""
        checks = []
        
        # Data encryption check
        encryption_passed = bool(submission.data_encryption_method)
        checks.append(SecurityCheck(
            check_type=SecurityCheckType.DATA_ENCRYPTION,
            passed=encryption_passed,
            title="Data Encryption",
            description=f"Encryption method: {submission.data_encryption_method or 'Not specified'}",
            recommendation=None if encryption_passed else "Implement encryption at rest and in transit using AES-256 or equivalent."
        ))
        
        # Access control check
        access_control_passed = bool(submission.access_control_mechanism)
        checks.append(SecurityCheck(
            check_type=SecurityCheckType.ACCESS_CONTROL,
            passed=access_control_passed,
            title="Access Control",
            description=f"Access control: {submission.access_control_mechanism or 'Not specified'}",
            recommendation=None if access_control_passed else "Implement role-based access control (RBAC) with principle of least privilege."
        ))
        
        # Compliance check
        compliance_passed = len(submission.compliance_certifications) > 0
        checks.append(SecurityCheck(
            check_type=SecurityCheckType.COMPLIANCE,
            passed=compliance_passed,
            title="Compliance Certifications",
            description=f"Certifications: {', '.join(submission.compliance_certifications) if submission.compliance_certifications else 'None'}",
            recommendation=None if compliance_passed else "Obtain relevant compliance certifications (e.g., SOC2, ISO27001, GDPR)."
        ))
        
        return checks
    
    def _calculate_score(self, findings: List[Finding], security_checks: List[SecurityCheck]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not findings and not security_checks:
            return 0.0
        
        # Score based on findings
        finding_score = 0.0
        if findings:
            compliant_count = sum(1 for f in findings if f.compliant)
            finding_score = (compliant_count / len(findings)) * 70  # 70% weight
        
        # Score based on security checks
        security_score = 0.0
        if security_checks:
            passed_count = sum(1 for c in security_checks if c.passed)
            security_score = (passed_count / len(security_checks)) * 30  # 30% weight
        
        return round(finding_score + security_score, 2)
    
    def _determine_status(self, score: float, findings: List[Finding]) -> str:
        """Determine overall review status."""
        critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL and not f.compliant]
        
        if critical_findings:
            return "Rejected - Critical Issues"
        elif score >= 80:
            return "Approved"
        elif score >= 60:
            return "Approved with Conditions"
        else:
            return "Rejected - Insufficient Compliance"
    
    async def _generate_executive_summary(
        self,
        submission: AIReviewSubmission,
        findings: List[Finding],
        security_checks: List[SecurityCheck],
        score: float
    ) -> str:
        """Generate executive summary using AI."""
        non_compliant = [f for f in findings if not f.compliant]
        failed_checks = [c for c in security_checks if not c.passed]
        
        summary = f"""
        ## Executive Summary
        
        **Project:** {submission.project_name}
        **Review Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
        **Overall Score:** {score}/100
        
        This AI solution has been reviewed against Microsoft's Responsible AI Standards and security best practices.
        
        **Key Findings:**
        - Total Findings: {len(findings)}
        - Non-Compliant Areas: {len(non_compliant)}
        - Failed Security Checks: {len(failed_checks)}
        
        **Status:** {'Requires immediate attention' if score < 60 else 'Meets acceptable standards' if score < 80 else 'Exceeds expectations'}
        """
        
        return summary.strip()
    
    def _extract_key_risks(self, findings: List[Finding]) -> List[str]:
        """Extract key risks from findings."""
        risks = []
        critical_findings = [f for f in findings if f.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH] and not f.compliant]
        
        for finding in critical_findings[:5]:  # Top 5 risks
            risks.append(f"{finding.title}: {finding.description}")
        
        return risks
    
    def _extract_recommendations(self, findings: List[Finding], security_checks: List[SecurityCheck]) -> List[str]:
        """Extract actionable recommendations."""
        recommendations = []
        
        # From findings
        for finding in findings:
            if not finding.compliant and finding.recommendation:
                recommendations.append(finding.recommendation)
        
        # From security checks
        for check in security_checks:
            if not check.passed and check.recommendation:
                recommendations.append(check.recommendation)
        
        return list(set(recommendations))  # Remove duplicates


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Process AI review for a submission.
    
    Request Body:
    {
        "submission_id": "uuid"
    }
    """
    logger.info('Processing AI review request')
    
    try:
        req_body = req.get_json()
        submission_id = req_body.get('submission_id')
        
        if not submission_id:
            return func.HttpResponse(
                body=json.dumps({"error": "submission_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Retrieve submission from Cosmos DB
        cosmos_client = get_cosmos_client()
        if not cosmos_client:
            return func.HttpResponse(
                body=json.dumps({"error": "Database service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )
        
        database = cosmos_client.get_database_client(settings.cosmos_db_database_name)
        container = database.get_container_client(settings.cosmos_db_container_name)
        
        submission_data = container.read_item(item=submission_id, partition_key=submission_id)
        submission = AIReviewSubmission(**submission_data)
        
        # Perform review
        review_engine = ResponsibleAIReviewEngine()
        review_result = await review_engine.review_submission(submission)
        
        # Store review result
        container.create_item(body=review_result.dict())
        
        return func.HttpResponse(
            body=json.dumps({
                "message": "Review completed successfully",
                "review_id": review_result.review_id,
                "overall_status": review_result.overall_status,
                "overall_score": review_result.overall_score
            }),
            status_code=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        logger.error(f"Error processing review: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
