import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List, Optional

# Environment variables for email configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
TO_EMAIL = os.environ.get("TO_EMAIL", "")

# Email templates
EMAIL_TEMPLATES = {
    "high_impact_alert": {
        "subject": "🚨 HIGH IMPACT EVENT: {ticker} Alert",
        "template": """HIGH IMPACT EVENT DETECTED

Ticker: {ticker}
Current Price: ${current_price}
Volatility: {volatility} (>{threshold} threshold)
Impact Level: {impact_level}
Timestamp: {timestamp}

{additional_info}

This is an automated alert from the Multi-Agent Portfolio Analysis System.
High impact event detected requiring immediate attention.

---
Multi-Agent Portfolio Analysis System
Powered by Vercel Serverless Functions"""
    },
    "portfolio_risk_alert": {
        "subject": "📊 PORTFOLIO RISK ALERT: {risk_level} Risk Detected",
        "template": """PORTFOLIO RISK ALERT

Risk Level: {risk_level}
High Risk Stocks: {high_risk_count}/{total_stocks}
Timestamp: {timestamp}

RISK BREAKDOWN:
{risk_breakdown}

RECOMMENDED ACTIONS:
{recommendations}

---
Multi-Agent Portfolio Analysis System
Portfolio Risk Management"""
    },
    "daily_summary": {
        "subject": "📈 Daily Portfolio Analysis Summary",
        "template": """DAILY PORTFOLIO ANALYSIS COMPLETED

Analysis Summary:
• Portfolio Size: {portfolio_size} stocks
• Analysis Duration: {duration} seconds
• High Impact Events: {high_impact_count}
• Timestamp: {timestamp}

{summary_details}

---
Multi-Agent Portfolio Analysis System
Daily Analysis Report"""
    },
    "system_alert": {
        "subject": "⚠️ SYSTEM ALERT: {alert_type}",
        "template": """SYSTEM ALERT

Alert Type: {alert_type}
Severity: {severity}
Timestamp: {timestamp}

DETAILS:
{details}

ACTION REQUIRED:
{action_required}

---
Multi-Agent Portfolio Analysis System
System Monitoring"""
    }
}

def send_email(to_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Core email sending function"""
    try:
        # Validate email configuration
        if not all([SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER]):
            return {
                "success": False,
                "error": "Email configuration incomplete - check environment variables"
            }
        
        # Create message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        text = message.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        
        return {
            "success": True,
            "message": f"Email sent successfully to {to_email}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def send_templated_email(template_name: str, recipient: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send email using predefined templates"""
    try:
        if template_name not in EMAIL_TEMPLATES:
            return {
                "success": False,
                "error": f"Template '{template_name}' not found",
                "available_templates": list(EMAIL_TEMPLATES.keys())
            }
        
        template = EMAIL_TEMPLATES[template_name]
        
        # Format subject and body
        subject = template["subject"].format(**template_data)
        body = template["template"].format(**template_data)
        
        # Send email
        result = send_email(recipient, subject, body)
        result["template_used"] = template_name
        
        return result
        
    except KeyError as e:
        return {
            "success": False,
            "error": f"Missing template data: {str(e)}",
            "template_name": template_name
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "template_name": template_name
        }

def send_high_impact_alert(ticker: str, current_price: float, volatility: float, impact_level: str, additional_info: str = "") -> Dict[str, Any]:
    """Send high impact event alert"""
    template_data = {
        "ticker": ticker,
        "current_price": f"{current_price:.2f}",
        "volatility": f"{volatility:.4f}",
        "threshold": "0.05",
        "impact_level": impact_level,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "additional_info": additional_info or "AI agents are analyzing this event and will provide detailed insights."
    }
    
    return send_templated_email("high_impact_alert", TO_EMAIL, template_data)

def send_portfolio_risk_alert(risk_level: str, high_risk_count: int, total_stocks: int, risk_breakdown: str, recommendations: str) -> Dict[str, Any]:
    """Send portfolio risk alert"""
    template_data = {
        "risk_level": risk_level,
        "high_risk_count": high_risk_count,
        "total_stocks": total_stocks,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "risk_breakdown": risk_breakdown,
        "recommendations": recommendations
    }
    
    return send_templated_email("portfolio_risk_alert", TO_EMAIL, template_data)

def send_daily_summary(portfolio_size: int, duration: float, high_impact_count: int, summary_details: str) -> Dict[str, Any]:
    """Send daily analysis summary"""
    template_data = {
        "portfolio_size": portfolio_size,
        "duration": f"{duration:.1f}",
        "high_impact_count": high_impact_count,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "summary_details": summary_details
    }
    
    return send_templated_email("daily_summary", TO_EMAIL, template_data)

def send_system_alert(alert_type: str, severity: str, details: str, action_required: str) -> Dict[str, Any]:
    """Send system alert"""
    template_data = {
        "alert_type": alert_type,
        "severity": severity,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "details": details,
        "action_required": action_required
    }
    
    return send_templated_email("system_alert", TO_EMAIL, template_data)

def send_bulk_notifications(notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Send multiple notifications in batch"""
    try:
        results = []
        success_count = 0
        failure_count = 0
        
        for notification in notifications:
            notification_type = notification.get("type", "custom")
            recipient = notification.get("recipient", TO_EMAIL)
            
            if notification_type == "high_impact":
                result = send_high_impact_alert(**notification.get("data", {}))
            elif notification_type == "portfolio_risk":
                result = send_portfolio_risk_alert(**notification.get("data", {}))
            elif notification_type == "daily_summary":
                result = send_daily_summary(**notification.get("data", {}))
            elif notification_type == "system_alert":
                result = send_system_alert(**notification.get("data", {}))
            elif notification_type == "custom":
                subject = notification.get("subject", "Notification")
                body = notification.get("body", "")
                result = send_email(recipient, subject, body)
            else:
                result = {"success": False, "error": f"Unknown notification type: {notification_type}"}
            
            results.append(result)
            if result["success"]:
                success_count += 1
            else:
                failure_count += 1
        
        return {
            "total_notifications": len(notifications),
            "success_count": success_count,
            "failure_count": failure_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_email_configuration() -> Dict[str, Any]:
    """Test email configuration"""
    try:
        # Check configuration
        config_status = {
            "smtp_server": bool(SMTP_SERVER),
            "smtp_port": bool(SMTP_PORT),
            "sender_email": bool(SENDER_EMAIL),
            "sender_password": bool(SENDER_PASSWORD),
            "to_email": bool(TO_EMAIL)
        }
        
        missing_config = [key for key, value in config_status.items() if not value]
        
        if missing_config:
            return {
                "success": False,
                "error": "Email configuration incomplete",
                "missing_config": missing_config,
                "config_status": config_status
            }
        
        # Send test email
        test_result = send_email(
            TO_EMAIL,
            "Test Email - Portfolio Analysis System",
            f"""Test email from Multi-Agent Portfolio Analysis System

This is a test email to verify email configuration.

Configuration Status:
• SMTP Server: {SMTP_SERVER}
• SMTP Port: {SMTP_PORT}
• Sender Email: {SENDER_EMAIL}
• Recipient Email: {TO_EMAIL}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you received this email, the configuration is working correctly.

---
Multi-Agent Portfolio Analysis System
Email Configuration Test"""
        )
        
        return {
            "config_status": config_status,
            "test_result": test_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def handler(request):
    """Vercel serverless function handler for email notifications"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "send_email")
            
            if action == "send_email":
                to_email = body.get("to_email", TO_EMAIL)
                subject = body.get("subject", "Notification")
                email_body = body.get("body", "")
                return json.dumps(send_email(to_email, subject, email_body))
            
            elif action == "send_templated":
                template_name = body.get("template_name", "")
                recipient = body.get("recipient", TO_EMAIL)
                template_data = body.get("template_data", {})
                return json.dumps(send_templated_email(template_name, recipient, template_data))
            
            elif action == "high_impact_alert":
                return json.dumps(send_high_impact_alert(**body.get("data", {})))
            
            elif action == "portfolio_risk_alert":
                return json.dumps(send_portfolio_risk_alert(**body.get("data", {})))
            
            elif action == "daily_summary":
                return json.dumps(send_daily_summary(**body.get("data", {})))
            
            elif action == "system_alert":
                return json.dumps(send_system_alert(**body.get("data", {})))
            
            elif action == "bulk_notifications":
                notifications = body.get("notifications", [])
                return json.dumps(send_bulk_notifications(notifications))
            
            elif action == "test_config":
                return json.dumps(test_email_configuration())
            
            else:
                return json.dumps({
                    "error": "Invalid action",
                    "available_actions": [
                        "send_email", "send_templated", "high_impact_alert",
                        "portfolio_risk_alert", "daily_summary", "system_alert",
                        "bulk_notifications", "test_config"
                    ]
                })
        
        else:
            return json.dumps({
                "service": "EmailHandler",
                "description": "Handles email notifications for portfolio analysis events",
                "templates": list(EMAIL_TEMPLATES.keys()),
                "endpoints": [
                    "POST - send_email: Send custom email",
                    "POST - send_templated: Send templated email",
                    "POST - high_impact_alert: Send high impact alert",
                    "POST - portfolio_risk_alert: Send portfolio risk alert",
                    "POST - daily_summary: Send daily summary",
                    "POST - system_alert: Send system alert",
                    "POST - bulk_notifications: Send multiple notifications",
                    "POST - test_config: Test email configuration"
                ],
                "status": "active"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "service": "EmailHandler"}) 