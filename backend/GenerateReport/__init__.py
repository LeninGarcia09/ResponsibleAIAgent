"""
Azure Function: Generate Review Report
Endpoint: POST /api/generate-report
"""
import azure.functions as func
import json
import logging
from datetime import datetime
from io import BytesIO
from typing import Optional
from shared.models import ReviewResult
from shared.azure_clients import get_cosmos_client, get_blob_client, get_graph_client
from shared.config import settings
import requests

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate HTML and PDF reports for AI reviews."""
    
    def __init__(self):
        self.blob_client = get_blob_client()
    
    def generate_html_report(self, review: ReviewResult, submission_data: dict) -> str:
        """Generate HTML report from review results."""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Responsible AI Review Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                }}
                .metadata {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metadata-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .metadata-card h3 {{
                    margin: 0 0 10px 0;
                    color: #0078d4;
                    font-size: 14px;
                    text-transform: uppercase;
                }}
                .metadata-card p {{
                    margin: 0;
                    font-size: 18px;
                    font-weight: bold;
                }}
                .score {{
                    font-size: 48px;
                    font-weight: bold;
                    color: {self._get_score_color(review.overall_score)};
                }}
                .status {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    background-color: {self._get_status_color(review.overall_status)};
                    color: white;
                }}
                .section {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .section h2 {{
                    color: #0078d4;
                    border-bottom: 2px solid #0078d4;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .finding {{
                    border-left: 4px solid #ddd;
                    padding: 15px;
                    margin-bottom: 15px;
                    background-color: #f9f9f9;
                    border-radius: 4px;
                }}
                .finding.critical {{
                    border-left-color: #d13438;
                    background-color: #fff5f5;
                }}
                .finding.high {{
                    border-left-color: #ff8c00;
                    background-color: #fff9f5;
                }}
                .finding.medium {{
                    border-left-color: #ffb900;
                    background-color: #fffdf5;
                }}
                .finding.low {{
                    border-left-color: #0078d4;
                    background-color: #f5faff;
                }}
                .finding.info {{
                    border-left-color: #107c10;
                    background-color: #f5fff5;
                }}
                .finding h4 {{
                    margin: 0 0 10px 0;
                    color: #333;
                }}
                .severity-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                    margin-left: 10px;
                }}
                .severity-badge.critical {{
                    background-color: #d13438;
                    color: white;
                }}
                .severity-badge.high {{
                    background-color: #ff8c00;
                    color: white;
                }}
                .severity-badge.medium {{
                    background-color: #ffb900;
                    color: #333;
                }}
                .severity-badge.low {{
                    background-color: #0078d4;
                    color: white;
                }}
                .severity-badge.info {{
                    background-color: #107c10;
                    color: white;
                }}
                .check {{
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    margin-bottom: 10px;
                    border-radius: 4px;
                    background-color: #f9f9f9;
                }}
                .check.passed {{
                    border-left: 4px solid #107c10;
                }}
                .check.failed {{
                    border-left: 4px solid #d13438;
                }}
                .check-icon {{
                    font-size: 24px;
                    margin-right: 15px;
                }}
                .recommendations {{
                    list-style-type: none;
                    padding: 0;
                }}
                .recommendations li {{
                    padding: 10px;
                    margin-bottom: 10px;
                    background-color: #f5faff;
                    border-left: 4px solid #0078d4;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 Responsible AI Review Report</h1>
                <p>Microsoft Responsible AI Standards Compliance Review</p>
            </div>
            
            <div class="metadata">
                <div class="metadata-card">
                    <h3>Review ID</h3>
                    <p>{review.review_id}</p>
                </div>
                <div class="metadata-card">
                    <h3>Project Name</h3>
                    <p>{submission_data.get('project_name', 'N/A')}</p>
                </div>
                <div class="metadata-card">
                    <h3>Review Date</h3>
                    <p>{review.review_date.strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                <div class="metadata-card">
                    <h3>Overall Score</h3>
                    <p class="score">{review.overall_score}</p>
                </div>
                <div class="metadata-card">
                    <h3>Status</h3>
                    <p><span class="status">{review.overall_status}</span></p>
                </div>
                <div class="metadata-card">
                    <h3>Submitter</h3>
                    <p>{submission_data.get('submitter_name', 'N/A')}</p>
                </div>
            </div>
            
            <div class="section">
                <h2>📋 Executive Summary</h2>
                {review.executive_summary.replace('\\n', '<br>')}
            </div>
            
            <div class="section">
                <h2>🎯 Responsible AI Findings</h2>
                {self._generate_findings_html(review.responsible_ai_findings)}
            </div>
            
            <div class="section">
                <h2>🔒 Security Checks</h2>
                {self._generate_security_checks_html(review.security_checks)}
            </div>
            
            <div class="section">
                <h2>⚠️ Key Risks</h2>
                <ul class="recommendations">
                    {''.join([f'<li>{risk}</li>' for risk in review.key_risks]) if review.key_risks else '<li>No critical risks identified</li>'}
                </ul>
            </div>
            
            <div class="section">
                <h2>💡 Recommendations</h2>
                <ul class="recommendations">
                    {''.join([f'<li>{rec}</li>' for rec in review.recommendations]) if review.recommendations else '<li>No additional recommendations</li>'}
                </ul>
            </div>
            
            <div class="section">
                <h2>✅ Compliance Summary</h2>
                <h3 style="color: #107c10;">Compliant Principles:</h3>
                <ul>
                    {''.join([f'<li>{p}</li>' for p in review.compliant_principles]) if review.compliant_principles else '<li>None</li>'}
                </ul>
                <h3 style="color: #d13438;">Non-Compliant Principles:</h3>
                <ul>
                    {''.join([f'<li>{p}</li>' for p in review.non_compliant_principles]) if review.non_compliant_principles else '<li>None</li>'}
                </ul>
            </div>
            
            <div class="footer">
                <p>Generated by {review.generated_by} | Confidential - Microsoft Internal Use Only</p>
                <p>© {datetime.now().year} Microsoft Corporation. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        return html_template
    
    def _generate_findings_html(self, findings) -> str:
        """Generate HTML for findings list."""
        if not findings:
            return "<p>No findings to report.</p>"
        
        html = ""
        for finding in findings:
            html += f"""
            <div class="finding {finding.severity.value}">
                <h4>
                    {finding.title}
                    <span class="severity-badge {finding.severity.value}">{finding.severity.value}</span>
                </h4>
                <p><strong>Principle:</strong> {finding.principle}</p>
                <p><strong>Description:</strong> {finding.description}</p>
                <p><strong>Recommendation:</strong> {finding.recommendation}</p>
                <p><strong>Compliant:</strong> {'✅ Yes' if finding.compliant else '❌ No'}</p>
            </div>
            """
        return html
    
    def _generate_security_checks_html(self, checks) -> str:
        """Generate HTML for security checks."""
        if not checks:
            return "<p>No security checks performed.</p>"
        
        html = ""
        for check in checks:
            status_class = "passed" if check.passed else "failed"
            icon = "✅" if check.passed else "❌"
            html += f"""
            <div class="check {status_class}">
                <span class="check-icon">{icon}</span>
                <div>
                    <h4 style="margin: 0 0 5px 0;">{check.title}</h4>
                    <p style="margin: 0;"><strong>Type:</strong> {check.check_type.value}</p>
                    <p style="margin: 5px 0 0 0;">{check.description}</p>
                    {f'<p style="margin: 5px 0 0 0; color: #d13438;"><strong>Recommendation:</strong> {check.recommendation}</p>' if check.recommendation else ''}
                </div>
            </div>
            """
        return html
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score."""
        if score >= 80:
            return "#107c10"
        elif score >= 60:
            return "#ffb900"
        else:
            return "#d13438"
    
    def _get_status_color(self, status: str) -> str:
        """Get color based on status."""
        if "Approved" in status and "Conditions" not in status:
            return "#107c10"
        elif "Conditions" in status:
            return "#ffb900"
        else:
            return "#d13438"
    
    async def upload_report_to_blob(self, report_html: str, review_id: str) -> Optional[str]:
        """Upload report to Azure Blob Storage."""
        try:
            if not self.blob_client:
                logger.error("Blob client not initialized")
                return None
            
            container_client = self.blob_client.get_container_client(settings.storage_container_reports)
            
            # Create container if it doesn't exist
            try:
                container_client.create_container()
            except:
                pass  # Container already exists
            
            # Upload HTML report
            blob_name = f"{review_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.html"
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(report_html, overwrite=True)
            
            # Get URL
            report_url = blob_client.url
            logger.info(f"Report uploaded successfully: {report_url}")
            return report_url
        
        except Exception as e:
            logger.error(f"Error uploading report to blob: {str(e)}")
            return None


async def send_email_notification(review: ReviewResult, submission_data: dict, report_url: str):
    """Send email notification via Microsoft Graph API."""
    try:
        graph = get_graph_client()
        if not graph:
            logger.error("Graph client not initialized")
            return False
        
        token = graph["token"]
        
        # Email content
        email_body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <h2>Responsible AI Review Completed</h2>
            <p>Dear {submission_data.get('submitter_name', 'User')},</p>
            <p>The Responsible AI review for your project <strong>{submission_data.get('project_name', 'N/A')}</strong> has been completed.</p>
            
            <h3>Review Summary:</h3>
            <ul>
                <li><strong>Review ID:</strong> {review.review_id}</li>
                <li><strong>Overall Score:</strong> {review.overall_score}/100</li>
                <li><strong>Status:</strong> {review.overall_status}</li>
                <li><strong>Review Date:</strong> {review.review_date.strftime('%Y-%m-%d %H:%M')}</li>
            </ul>
            
            <p>You can access the full report here: <a href="{report_url}">View Report</a></p>
            
            <p>If you have any questions, please contact the Responsible AI team.</p>
            
            <p>Best regards,<br>
            Responsible AI Agent</p>
            
            <hr>
            <p style="font-size: 12px; color: #666;">This is an automated message. Please do not reply to this email.</p>
        </body>
        </html>
        """
        
        # Prepare email
        email_data = {
            "message": {
                "subject": f"{settings.email_subject_prefix} Review Completed - {submission_data.get('project_name', 'N/A')}",
                "body": {
                    "contentType": "HTML",
                    "content": email_body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": submission_data.get('submitter_email', '')
                        }
                    }
                ],
                "from": {
                    "emailAddress": {
                        "address": settings.email_from
                    }
                }
            },
            "saveToSentItems": "true"
        }
        
        # Send email via Microsoft Graph API
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://graph.microsoft.com/v1.0/users/{user-id}/sendMail",  # Replace with actual user ID or use /me/
            headers=headers,
            json=email_data
        )
        
        if response.status_code == 202:
            logger.info(f"Email sent successfully to {submission_data.get('submitter_email')}")
            return True
        else:
            logger.error(f"Failed to send email: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate and send review report.
    
    Request Body:
    {
        "review_id": "REV-20231201120000"
    }
    """
    logger.info('Processing report generation request')
    
    try:
        req_body = req.get_json()
        review_id = req_body.get('review_id')
        
        if not review_id:
            return func.HttpResponse(
                body=json.dumps({"error": "review_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Retrieve review from Cosmos DB
        cosmos_client = get_cosmos_client()
        if not cosmos_client:
            return func.HttpResponse(
                body=json.dumps({"error": "Database service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )
        
        database = cosmos_client.get_database_client(settings.cosmos_db_database_name)
        container = database.get_container_client(settings.cosmos_db_container_name)
        
        # Query for review
        query = f"SELECT * FROM c WHERE c.review_id = '{review_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not items:
            return func.HttpResponse(
                body=json.dumps({"error": "Review not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        review_data = items[0]
        review = ReviewResult(**review_data)
        
        # Get submission data
        submission_query = f"SELECT * FROM c WHERE c.id = '{review.submission_id}'"
        submission_items = list(container.query_items(query=submission_query, enable_cross_partition_query=True))
        submission_data = submission_items[0] if submission_items else {}
        
        # Generate report
        report_gen = ReportGenerator()
        report_html = report_gen.generate_html_report(review, submission_data)
        
        # Upload to blob storage
        report_url = await report_gen.upload_report_to_blob(report_html, review_id)
        
        # Update review with report URL
        if report_url:
            review.report_url = report_url
            review.report_html = report_html
            container.upsert_item(body=review.dict())
        
        # Send email notification
        if settings.enable_email_notifications:
            await send_email_notification(review, submission_data, report_url or "")
        
        return func.HttpResponse(
            body=json.dumps({
                "message": "Report generated successfully",
                "review_id": review_id,
                "report_url": report_url
            }),
            status_code=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
