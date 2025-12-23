"""
Email notification service for Vizion.
Sends notifications to users about their analyses.
"""

import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta
import os


def send_email(to_email, subject, html_content):
    """
    Send email using SendGrid.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get SendGrid API key from secrets or environment
        api_key = None
        
        try:
            if "sendgrid" in st.secrets:
                api_key = st.secrets["sendgrid"]["api_key"]
                from_email = st.secrets["sendgrid"].get("from_email", "noreply@vizion.app")
        except:
            pass
        
        if not api_key:
            api_key = os.getenv("SENDGRID_API_KEY")
            from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@vizion.app")
        
        if not api_key:
            print("SendGrid API key not configured. Email not sent.")
            return False
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        return response.status_code == 202
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_welcome_email(user):
    """Send welcome email to new user."""
    subject = "Welcome to Vizion!"
    
    html_content = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    background: #38BDF8;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .feature {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 3px solid #38BDF8;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to Vizion!</h1>
            </div>
            <div class="content">
                <p>Hi {user.name},</p>
                
                <p>Thanks for joining Vizion! We're excited to help you analyze your data with AI-powered insights.</p>
                
                <h3>What you can do with Vizion:</h3>
                
                <div class="feature">
                    <strong>Upload & Analyze</strong><br>
                    Upload CSV files and get instant insights with visualizations and statistics
                </div>
                
                <div class="feature">
                    <strong>ML Notebooks</strong><br>
                    Generate Jupyter notebooks with machine learning models tailored to your data
                </div>
                
                <div class="feature">
                    <strong>Data Cleaning</strong><br>
                    Automatically clean and prepare your data for analysis
                </div>
                
                <div class="feature">
                    <strong>Professional Reports</strong><br>
                    Download PDF and HTML reports of your analyses
                </div>
                
                <a href="https://your-app-url.streamlit.app" class="button">Get Started Now</a>
                
                <p>Need help? Just reply to this email and we'll be happy to assist!</p>
                
                <p>Best regards,<br>The Vizion Team</p>
            </div>
        </body>
    </html>
    """
    
    return send_email(user.email, subject, html_content)


def send_analysis_complete_email(user, dataset_name, analysis_summary):
    """Send notification when analysis is complete."""
    subject = f"Your analysis of '{dataset_name}' is ready!"
    
    html_content = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    background: #38BDF8;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .stats {{
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Analysis Complete!</h1>
            </div>
            <div class="content">
                <p>Hi {user.name},</p>
                
                <p>Great news! Your analysis of <strong>{dataset_name}</strong> is complete.</p>
                
                <div class="stats">
                    <h3>Analysis Summary:</h3>
                    {analysis_summary}
                </div>
                
                <a href="https://your-app-url.streamlit.app" class="button">View Results</a>
                
                <p>Your analysis includes:</p>
                <ul>
                    <li>Statistical insights and visualizations</li>
                    <li>ML model recommendations</li>
                    <li>Downloadable reports (PDF/HTML)</li>
                    <li>Generated Jupyter notebooks</li>
                </ul>
                
                <p>Best regards,<br>The Vizion Team</p>
            </div>
        </body>
    </html>
    """
    
    return send_email(user.email, subject, html_content)


def send_ml_notebook_ready_email(user, dataset_name, model_type, accuracy):
    """Send notification when ML notebook execution is complete."""
    subject = f"ML Model Ready: {model_type} for '{dataset_name}'"
    
    accuracy_text = f"{accuracy:.2%}" if accuracy else "See results"
    
    html_content = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    background: #38BDF8;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .metric {{
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 15px 0;
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #10b981;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ML Model Trained!</h1>
            </div>
            <div class="content">
                <p>Hi {user.name},</p>
                
                <p>Your <strong>{model_type}</strong> model for <strong>{dataset_name}</strong> has been trained successfully!</p>
                
                <div class="metric">
                    <div>Model Performance</div>
                    <div class="metric-value">{accuracy_text}</div>
                </div>
                
                <a href="https://your-app-url.streamlit.app" class="button">View Model Details</a>
                
                <p>You can now:</p>
                <ul>
                    <li>Download the trained notebook (.ipynb)</li>
                    <li>Export as Python script (.py)</li>
                    <li>Generate PDF model card</li>
                    <li>View detailed metrics and visualizations</li>
                </ul>
                
                <p>Best regards,<br>The Vizion Team</p>
            </div>
        </body>
    </html>
    """
    
    return send_email(user.email, subject, html_content)


def can_send_notification(user):
    """
    Check if we can send a notification to the user.
    Implements rate limiting to avoid spam.
    """
    # Check if notifications are enabled
    if user.email_notifications != 'true':
        return False
    
    # Check rate limit (max 1 email per 5 minutes)
    if user.last_notification_sent:
        time_since_last = datetime.utcnow() - user.last_notification_sent
        if time_since_last < timedelta(minutes=5):
            return False
    
    return True


def mark_notification_sent(session, user):
    """Update user's last notification timestamp."""
    user.last_notification_sent = datetime.utcnow()
    session.commit()
