#!/usr/bin/env python3
"""
Enhanced Email Service with Multi-Provider Fallback
Designed for Vercel serverless compatibility with SendGrid, Resend, and SMTP fallbacks
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class EmailProvider:
    """Base class for email providers"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if provider is available"""
        return True
    
    def send_email(self, to_email: str, subject: str, html_content: str, plain_content: str = None) -> Dict[str, Any]:
        """Send email - to be implemented by subclasses"""
        raise NotImplementedError

class SendGridProvider(EmailProvider):
    """SendGrid email provider"""
    
    def __init__(self):
        super().__init__("sendgrid")
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('SENDGRID_FROM_EMAIL')
    
    def _check_availability(self) -> bool:
        """Check if SendGrid is configured"""
        return bool(self.api_key and self.from_email)
    
    def send_email(self, to_email: str, subject: str, html_content: str, plain_content: str = None) -> Dict[str, Any]:
        """Send email using SendGrid API"""
        if not self.is_available:
            return {"success": False, "error": "SendGrid not configured"}
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content
            )
            
            sg = SendGridAPIClient(api_key=self.api_key)
            response = sg.send(message)
            
            return {
                "success": True,
                "provider": "sendgrid",
                "status_code": response.status_code,
                "message": "Email sent successfully via SendGrid"
            }
            
        except ImportError:
            return {"success": False, "error": "SendGrid library not installed"}
        except Exception as e:
            return {"success": False, "error": f"SendGrid error: {str(e)}"}

class ResendProvider(EmailProvider):
    """Resend email provider"""
    
    def __init__(self):
        super().__init__("resend")
        self.api_key = os.environ.get('RESEND_API_KEY')
        self.from_email = os.environ.get('RESEND_FROM_EMAIL')
    
    def _check_availability(self) -> bool:
        """Check if Resend is configured"""
        return bool(self.api_key and self.from_email)
    
    def send_email(self, to_email: str, subject: str, html_content: str, plain_content: str = None) -> Dict[str, Any]:
        """Send email using Resend API"""
        if not self.is_available:
            return {"success": False, "error": "Resend not configured"}
        
        try:
            import requests
            
            payload = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            if plain_content:
                payload["text"] = plain_content
            
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "provider": "resend",
                    "id": response.json().get("id"),
                    "message": "Email sent successfully via Resend"
                }
            else:
                return {
                    "success": False,
                    "error": f"Resend API error: {response.status_code} - {response.text}"
                }
                
        except ImportError:
            return {"success": False, "error": "Requests library not available"}
        except Exception as e:
            return {"success": False, "error": f"Resend error: {str(e)}"}

class SMTPProvider(EmailProvider):
    """SMTP email provider (Gmail, Outlook, etc.)"""
    
    def __init__(self):
        super().__init__("smtp")
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.sender_email = os.environ.get('SENDER_EMAIL')
        self.sender_password = os.environ.get('SENDER_PASSWORD')
    
    def _check_availability(self) -> bool:
        """Check if SMTP is configured"""
        return bool(self.sender_email and self.sender_password)
    
    def send_email(self, to_email: str, subject: str, html_content: str, plain_content: str = None) -> Dict[str, Any]:
        """Send email using SMTP"""
        if not self.is_available:
            return {"success": False, "error": "SMTP not configured"}
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message["From"] = self.sender_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add plain text part
            if plain_content:
                part1 = MIMEText(plain_content, 'plain')
                message.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_content, 'html')
            message.attach(part2)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            text = message.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()
            
            return {
                "success": True,
                "provider": "smtp",
                "message": f"Email sent successfully via SMTP ({self.smtp_server})"
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "error": "SMTP authentication failed - check credentials"
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "error": f"SMTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"SMTP connection error: {str(e)}"
            }

class EmailService:
    """Multi-provider email service with intelligent fallback"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.default_from_email = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')
        self.default_to_email = os.environ.get('TO_EMAIL', 'admin@example.com')
    
    def _initialize_providers(self) -> List[EmailProvider]:
        """Initialize available email providers in order of preference"""
        providers = []
        
        # Primary: SendGrid (most reliable for serverless)
        sendgrid = SendGridProvider()
        if sendgrid.is_available:
            providers.append(sendgrid)
        
        # Secondary: Resend (good alternative)
        resend = ResendProvider()
        if resend.is_available:
            providers.append(resend)
        
        # Fallback: SMTP (may fail in serverless)
        smtp = SMTPProvider()
        if smtp.is_available:
            providers.append(smtp)
        
        return providers
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all email providers"""
        status = {
            "available_providers": len(self.providers),
            "providers": {}
        }
        
        for provider in self.providers:
            status["providers"][provider.name] = {
                "available": provider.is_available,
                "primary": provider == self.providers[0] if self.providers else False
            }
        
        # Check for missing providers
        all_providers = ["sendgrid", "resend", "smtp"]
        missing_providers = []
        
        for provider_name in all_providers:
            if not any(p.name == provider_name for p in self.providers):
                missing_providers.append(provider_name)
        
        status["missing_providers"] = missing_providers
        status["recommendations"] = self._get_recommendations()
        
        return status
    
    def _get_recommendations(self) -> List[str]:
        """Get configuration recommendations"""
        recommendations = []
        
        if not self.providers:
            recommendations.append("Configure at least one email provider")
        
        if len(self.providers) == 1:
            recommendations.append("Configure multiple providers for redundancy")
        
        # Check for specific providers
        provider_names = [p.name for p in self.providers]
        
        if "sendgrid" not in provider_names:
            recommendations.append("Consider SendGrid for best serverless compatibility")
        
        if "resend" not in provider_names and "sendgrid" not in provider_names:
            recommendations.append("Configure Resend as modern alternative to SMTP")
        
        return recommendations
    
    def send_email(self, to_email: str = None, subject: str = "", html_content: str = "", plain_content: str = None) -> Dict[str, Any]:
        """Send email with provider fallback"""
        if not to_email:
            to_email = self.default_to_email
        
        if not self.providers:
            return {
                "success": False,
                "error": "No email providers configured",
                "recommendations": ["Add SENDGRID_API_KEY, RESEND_API_KEY, or SMTP configuration"]
            }
        
        last_errors = []
        
        for i, provider in enumerate(self.providers):
            try:
                result = provider.send_email(to_email, subject, html_content, plain_content)
                
                if result.get("success"):
                    return {
                        "success": True,
                        "provider": provider.name,
                        "attempt": i + 1,
                        "total_providers": len(self.providers),
                        "message": result.get("message", "Email sent successfully")
                    }
                else:
                    last_errors.append(f"{provider.name}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                last_errors.append(f"{provider.name}: {str(e)}")
                continue
        
        return {
            "success": False,
            "error": "All email providers failed",
            "provider_errors": last_errors,
            "providers_attempted": len(self.providers)
        }
    
    def send_templated_email(self, template_name: str, template_data: Dict[str, Any], to_email: str = None) -> Dict[str, Any]:
        """Send templated email"""
        templates = self._get_email_templates()
        
        if template_name not in templates:
            return {
                "success": False,
                "error": f"Email template '{template_name}' not found",
                "available_templates": list(templates.keys())
            }
        
        template = templates[template_name]
        
        try:
            # Format subject and content
            subject = template["subject"].format(**template_data)
            html_content = template["html_template"].format(**template_data)
            plain_content = template.get("plain_template", "").format(**template_data)
            
            return self.send_email(to_email, subject, html_content, plain_content)
            
        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing template variable: {e}",
                "required_variables": template.get("required_variables", [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Template formatting error: {str(e)}"
            }
    
    def _get_email_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get email templates"""
        return {
            "high_impact_alert": {
                "subject": "🚨 HIGH IMPACT ALERT: {ticker} - {impact_level}",
                "html_template": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #dc3545; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">🚨 HIGH IMPACT EVENT DETECTED</h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #dc3545; margin-top: 0;">Stock Alert: {ticker}</h2>
                        
                        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <p><strong>Current Price:</strong> ${current_price}</p>
                            <p><strong>Volatility:</strong> {volatility} (Threshold: >{threshold})</p>
                            <p><strong>Impact Level:</strong> <span style="color: #dc3545; font-weight: bold;">{impact_level}</span></p>
                            <p><strong>Timestamp:</strong> {timestamp}</p>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                            <h3 style="margin-top: 0; color: #856404;">Additional Information</h3>
                            <p>{additional_info}</p>
                        </div>
                        
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                            <p style="color: #6c757d; font-size: 14px;">
                                This is an automated alert from the Multi-Agent Portfolio Analysis System.<br>
                                High impact event detected requiring immediate attention.
                            </p>
                        </div>
                    </div>
                </div>
                """,
                "plain_template": """
HIGH IMPACT EVENT DETECTED

Ticker: {ticker}
Current Price: ${current_price}
Volatility: {volatility} (>{threshold} threshold)
Impact Level: {impact_level}
Timestamp: {timestamp}

Additional Information:
{additional_info}

This is an automated alert from the Multi-Agent Portfolio Analysis System.
High impact event detected requiring immediate attention.
                """,
                "required_variables": ["ticker", "current_price", "volatility", "threshold", "impact_level", "timestamp", "additional_info"]
            },
            
            "portfolio_summary": {
                "subject": "📊 Portfolio Analysis Summary - {portfolio_size} stocks analyzed",
                "html_template": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #007bff; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">📊 Portfolio Analysis Complete</h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #007bff; margin-top: 0;">Analysis Summary</h2>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                            <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                                <h3 style="margin: 0; color: #007bff;">{portfolio_size}</h3>
                                <p style="margin: 5px 0; color: #6c757d;">Stocks Analyzed</p>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                                <h3 style="margin: 0; color: #dc3545;">{high_impact_count}</h3>
                                <p style="margin: 5px 0; color: #6c757d;">High Impact Events</p>
                            </div>
                        </div>
                        
                        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <h3 style="margin-top: 0;">Analysis Details</h3>
                            <p><strong>Duration:</strong> {duration} seconds</p>
                            <p><strong>Timestamp:</strong> {timestamp}</p>
                            <p><strong>Overall Risk:</strong> {overall_risk}</p>
                        </div>
                        
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                            <p style="color: #6c757d; font-size: 14px;">
                                Multi-Agent Portfolio Analysis System<br>
                                Automated Analysis Report
                            </p>
                        </div>
                    </div>
                </div>
                """,
                "plain_template": """
PORTFOLIO ANALYSIS COMPLETED

Analysis Summary:
• Portfolio Size: {portfolio_size} stocks
• High Impact Events: {high_impact_count}
• Analysis Duration: {duration} seconds
• Overall Risk: {overall_risk}
• Timestamp: {timestamp}

Multi-Agent Portfolio Analysis System
Automated Analysis Report
                """,
                "required_variables": ["portfolio_size", "high_impact_count", "duration", "timestamp", "overall_risk"]
            },
            
            "system_alert": {
                "subject": "⚠️ SYSTEM ALERT: {alert_type}",
                "html_template": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #ffc107; color: #212529; padding: 20px; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">⚠️ SYSTEM ALERT</h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #ffc107; margin-top: 0;">Alert: {alert_type}</h2>
                        
                        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <p><strong>Severity:</strong> {severity}</p>
                            <p><strong>Timestamp:</strong> {timestamp}</p>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                            <h3 style="margin-top: 0; color: #856404;">Details</h3>
                            <p>{details}</p>
                        </div>
                        
                        <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 4px solid #bee5eb;">
                            <h3 style="margin-top: 0; color: #0c5460;">Action Required</h3>
                            <p>{action_required}</p>
                        </div>
                        
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                            <p style="color: #6c757d; font-size: 14px;">
                                Multi-Agent Portfolio Analysis System<br>
                                System Monitoring Alert
                            </p>
                        </div>
                    </div>
                </div>
                """,
                "plain_template": """
SYSTEM ALERT

Alert Type: {alert_type}
Severity: {severity}
Timestamp: {timestamp}

Details:
{details}

Action Required:
{action_required}

Multi-Agent Portfolio Analysis System
System Monitoring Alert
                """,
                "required_variables": ["alert_type", "severity", "timestamp", "details", "action_required"]
            }
        }
    
    def test_configuration(self) -> Dict[str, Any]:
        """Test email configuration"""
        status = self.get_provider_status()
        
        if not self.providers:
            return {
                "success": False,
                "error": "No email providers configured",
                "status": status
            }
        
        # Test with each provider
        test_results = []
        
        for provider in self.providers:
            try:
                result = provider.send_email(
                    to_email=self.default_to_email,
                    subject="Test Email - Configuration Verification",
                    html_content="""
                    <h2>Email Configuration Test</h2>
                    <p>This is a test email to verify email configuration.</p>
                    <p><strong>Provider:</strong> {}</p>
                    <p><strong>Timestamp:</strong> {}</p>
                    <p>If you received this email, the configuration is working correctly.</p>
                    """.format(provider.name, datetime.now().isoformat()),
                    plain_content=f"""
Email Configuration Test

This is a test email to verify email configuration.

Provider: {provider.name}
Timestamp: {datetime.now().isoformat()}

If you received this email, the configuration is working correctly.
                    """
                )
                
                test_results.append({
                    "provider": provider.name,
                    "success": result.get("success", False),
                    "message": result.get("message", result.get("error", "Unknown result"))
                })
                
            except Exception as e:
                test_results.append({
                    "provider": provider.name,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": any(r["success"] for r in test_results),
            "test_results": test_results,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

# Global email service instance
email_service = EmailService()

def handler(request):
    """Vercel serverless function handler"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "send_email")
            
            if action == "send_email":
                return json.dumps(email_service.send_email(
                    to_email=body.get("to_email"),
                    subject=body.get("subject", ""),
                    html_content=body.get("html_content", ""),
                    plain_content=body.get("plain_content")
                ))
            
            elif action == "send_templated":
                return json.dumps(email_service.send_templated_email(
                    template_name=body.get("template_name"),
                    template_data=body.get("template_data", {}),
                    to_email=body.get("to_email")
                ))
            
            elif action == "test_config":
                return json.dumps(email_service.test_configuration())
            
            elif action == "get_status":
                return json.dumps(email_service.get_provider_status())
            
            else:
                return json.dumps({"error": "Unknown action"})
        
        elif request.method == "GET":
            return json.dumps(email_service.get_provider_status())
        
        else:
            return json.dumps({"error": "Method not allowed"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Test the email service
    service = EmailService()
    print("Email Service Status:")
    print(json.dumps(service.get_provider_status(), indent=2))
    
    # Test configuration
    print("\nTesting Configuration:")
    test_result = service.test_configuration()
    print(json.dumps(test_result, indent=2)) 