# File: app/services/email_service.py
import os
from email.message import EmailMessage
import aiosmtplib

async def dispatch_branch_email_notification(
    target_email: str, 
    branch_name: str, 
    patient_name: str, 
    service_type: str, 
    target_time: str, 
    patient_address: str
):
    """
    Asynchronously dispatches an urgent email notification to the branch command center.
    Utilizes aiosmtplib to prevent event loop blocking in FastAPI.
    """
    sender_email = os.environ.get("EMAIL_SENDER")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("⚠️ Dispatch Failed: SMTP credentials are missing in the .env configuration.")
        return

    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = target_email
    msg['Subject'] = f"🚨 URGENT: New {service_type} Order at {branch_name}"
    
    body = f"""Hello {branch_name} Command Center,

A new Homecare service order has been successfully ingested into the dispatch system.

📝 PATIENT DETAILS:
- Name: {patient_name}
- Address: {patient_address}
- Service Type: {service_type}
- Scheduled Time: {target_time}

Please monitor the dashboard and assign a field nurse immediately.

Best Regards,
TMC Automated Dispatch System
"""
    msg.set_content(body)
    
    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=sender_email,
            password=sender_password
        )
    except Exception as e:
        print(f"⚠️ Failed to send email to {target_email}: {str(e)}")