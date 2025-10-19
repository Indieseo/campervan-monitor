"""
Alert Delivery System
Sends notifications via Email, Slack, and SMS for critical price alerts
"""

import os
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import requests
from loguru import logger

BASE_DIR = Path(__file__).parent.resolve()


class AlertDelivery:
    """Manages multi-channel alert delivery"""
    
    def __init__(self):
        self.email_enabled = os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
        self.slack_enabled = os.getenv('ENABLE_SLACK_ALERTS', 'false').lower() == 'true'
        self.sms_enabled = os.getenv('ENABLE_SMS_ALERTS', 'false').lower() == 'true'
        
        # Email config
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '465'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.alert_recipients = os.getenv('ALERT_RECIPIENTS', '').split(',')
        
        # Slack config
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        
        # SMS config (Twilio)
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_from = os.getenv('TWILIO_PHONE_FROM', '')
        self.sms_recipients = os.getenv('SMS_RECIPIENTS', '').split(',')
    
    def send_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Send alerts through all enabled channels"""
        if not alerts:
            logger.info("No alerts to send")
            return {'email': False, 'slack': False, 'sms': False}
        
        results = {}
        
        # Filter critical alerts
        critical_alerts = [a for a in alerts if a.get('severity') == 'HIGH']
        
        # Email
        if self.email_enabled and self.alert_recipients[0]:
            results['email'] = self._send_email(alerts)
        
        # Slack
        if self.slack_enabled and self.slack_webhook:
            results['slack'] = self._send_slack(alerts)
        
        # SMS (only for critical)
        if self.sms_enabled and critical_alerts and self.sms_recipients[0]:
            results['sms'] = self._send_sms(critical_alerts)
        
        return results
    
    def _send_email(self, alerts: List[Dict[str, Any]]) -> bool:
        """Send email alert"""
        try:
            msg = EmailMessage()
            msg['Subject'] = self._create_email_subject(alerts)
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(self.alert_recipients)
            
            # Create HTML email
            html_body = self._create_email_body(alerts)
            msg.add_alternative(html_body, subtype='html')
            
            # Send via SMTP
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
                smtp.login(self.smtp_user, self.smtp_password)
                smtp.send_message(msg)
            
            logger.info(f"✅ Email alert sent to {len(self.alert_recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email alert failed: {e}")
            return False
    
    def _send_slack(self, alerts: List[Dict[str, Any]]) -> bool:
        """Send Slack webhook notification"""
        try:
            slack_message = self._create_slack_message(alerts)
            
            response = requests.post(
                self.slack_webhook,
                json=slack_message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Slack alert sent successfully")
                return True
            else:
                logger.error(f"❌ Slack alert failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Slack alert failed: {e}")
            return False
    
    def _send_sms(self, alerts: List[Dict[str, Any]]) -> bool:
        """Send SMS via Twilio (critical alerts only)"""
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_sid, self.twilio_token)
            sms_body = self._create_sms_body(alerts)
            
            for recipient in self.sms_recipients:
                if recipient.strip():
                    client.messages.create(
                        body=sms_body,
                        from_=self.twilio_from,
                        to=recipient.strip()
                    )
            
            logger.info(f"✅ SMS alerts sent to {len(self.sms_recipients)} recipients")
            return True
            
        except ImportError:
            logger.warning("⚠️  Twilio not installed. Run: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"❌ SMS alert failed: {e}")
            return False
    
    def _create_email_subject(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate email subject line"""
        critical_count = sum(1 for a in alerts if a.get('severity') == 'HIGH')
        
        if critical_count > 0:
            return f"🚨 {critical_count} Critical Price Alert(s) - Campervan Intel"
        else:
            return f"📊 {len(alerts)} Price Alert(s) - Campervan Intel"
    
    def _create_email_body(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate HTML email body"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; }}
                .alert {{ border-left: 4px solid #e74c3c; padding: 15px; margin: 10px 0; background: #f8f9fa; }}
                .alert.medium {{ border-left-color: #f39c12; }}
                .alert.low {{ border-left-color: #3498db; }}
                .severity {{ font-weight: bold; color: #e74c3c; }}
                .action {{ background: #ecf0f1; padding: 10px; margin: 10px 0; }}
                .impact {{ color: #27ae60; font-weight: bold; }}
                .footer {{ background: #ecf0f1; padding: 15px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚐 Campervan Competitive Intelligence Alert</h2>
                <p>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <div style="padding: 20px;">
                <h3>📊 {len(alerts)} Alert(s) Detected</h3>
        """
        
        for alert in alerts:
            severity_class = alert.get('severity', 'LOW').lower()
            severity_icon = '🚨' if alert.get('severity') == 'HIGH' else '⚠️' if alert.get('severity') == 'MEDIUM' else 'ℹ️'
            
            html += f"""
                <div class="alert {severity_class}">
                    <div class="severity">{severity_icon} {alert.get('severity', 'INFO')}</div>
                    <h4>{alert.get('message', 'No message')}</h4>
                    <div class="action">
                        <strong>Recommended Action:</strong><br>
                        {alert.get('action', 'No action specified')}
                    </div>
                    <div class="impact">
                        💰 Impact: {alert.get('impact', 'Unknown')}
                    </div>
                </div>
            """
        
        html += """
            </div>
            
            <div class="footer">
                <p><strong>🎯 What to do:</strong></p>
                <ol>
                    <li>Review the dashboard for detailed analysis</li>
                    <li>Assess each recommended action</li>
                    <li>Implement high-priority changes first</li>
                    <li>Monitor competitor responses</li>
                </ol>
                <p><em>Dashboard: http://localhost:8501</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_slack_message(self, alerts: List[Dict[str, Any]]) -> Dict:
        """Generate Slack message payload"""
        critical_count = sum(1 for a in alerts if a.get('severity') == 'HIGH')
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚐 {len(alerts)} Price Alert(s) Detected"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{datetime.now().strftime('%B %d, %Y at %I:%M %p')}*"
                    }
                ]
            },
            {"type": "divider"}
        ]
        
        for alert in alerts[:5]:  # Limit to 5 alerts in Slack
            severity_emoji = '🚨' if alert.get('severity') == 'HIGH' else '⚠️' if alert.get('severity') == 'MEDIUM' else 'ℹ️'
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{severity_emoji} {alert.get('severity')}:* {alert.get('message')}\n\n" +
                            f"*Action:* {alert.get('action')}\n" +
                            f"*Impact:* {alert.get('impact')}"
                }
            })
            blocks.append({"type": "divider"})
        
        if len(alerts) > 5:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_...and {len(alerts) - 5} more alerts_"
                }
            })
        
        return {"blocks": blocks}
    
    def _create_sms_body(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate SMS text (critical only, keep short)"""
        alert = alerts[0]  # First critical alert only
        return f"🚨 CAMPERVAN ALERT: {alert.get('message')[:100]}. Action: {alert.get('action')[:50]}. Check dashboard."
    
    def send_daily_summary(self, summary: Dict[str, Any]) -> bool:
        """Send daily summary email (non-urgent)"""
        if not self.email_enabled or not self.alert_recipients[0]:
            return False
        
        try:
            msg = EmailMessage()
            msg['Subject'] = f"📊 Daily Intelligence Summary - {datetime.now().strftime('%b %d, %Y')}"
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(self.alert_recipients)
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>🚐 Daily Competitive Intelligence Summary</h2>
                <p>{datetime.now().strftime('%B %d, %Y')}</p>
                
                <h3>📊 Key Metrics</h3>
                <ul>
                    <li><strong>Companies Monitored:</strong> {summary.get('companies_scraped', 0)}</li>
                    <li><strong>Prices Collected:</strong> {summary.get('prices_collected', 0)}</li>
                    <li><strong>Market Avg Price:</strong> €{summary.get('market_avg', 0):.2f}</li>
                    <li><strong>Your Position:</strong> {summary.get('market_position', 'N/A')}</li>
                </ul>
                
                <h3>🚨 Alerts Today</h3>
                <p>{summary.get('alerts_count', 0)} alert(s) detected</p>
                
                <p><a href="http://localhost:8501">View Dashboard</a></p>
            </body>
            </html>
            """
            
            msg.add_alternative(html_body, subtype='html')
            
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
                smtp.login(self.smtp_user, self.smtp_password)
                smtp.send_message(msg)
            
            logger.info("✅ Daily summary email sent")
            return True
            
        except Exception as e:
            logger.error(f"❌ Daily summary failed: {e}")
            return False


# Test function
if __name__ == "__main__":
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create test alerts
    test_alerts = [
        {
            'severity': 'HIGH',
            'message': 'Roadsurfer dropped prices by 15%',
            'action': 'Review pricing strategy and consider matching discount',
            'impact': '€12,000 potential revenue loss'
        },
        {
            'severity': 'MEDIUM',
            'message': 'McRent added new vehicle types',
            'action': 'Analyze new offerings and assess if we should expand fleet',
            'impact': 'Market share opportunity'
        }
    ]
    
    # Test delivery
    delivery = AlertDelivery()
    
    print("📧 Email enabled:", delivery.email_enabled)
    print("💬 Slack enabled:", delivery.slack_enabled)
    print("📱 SMS enabled:", delivery.sms_enabled)
    print()
    
    if delivery.email_enabled or delivery.slack_enabled:
        print("🧪 Sending test alerts...")
        results = delivery.send_alerts(test_alerts)
        print("Results:", results)
    else:
        print("⚠️  No delivery channels configured")
        print("   Set environment variables in .env file")
