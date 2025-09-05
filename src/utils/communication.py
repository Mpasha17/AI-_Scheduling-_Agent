import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import pandas as pd

# For a real implementation, we would use a proper SMS service like Twilio
# For this demo, we'll simulate SMS sending with logging

logger = logging.getLogger(__name__)

# Email configuration from environment variables
from ..config import (
    EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
)

def send_email(to_email, subject, body, attachments=None):
    """
    Send an email with optional attachments
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body (HTML format supported)
        attachments (list): List of file paths to attach
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'html'))
        
        # Attach files if provided
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    msg.attach(part)
                else:
                    logger.warning(f"Attachment file not found: {file_path}")
        
        # Connect to server and send
        if EMAIL_HOST and EMAIL_PORT and EMAIL_USERNAME and EMAIL_PASSWORD:
            server = smtplib.SMTP(EMAIL_HOST, int(EMAIL_PORT))
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        else:
            # If email settings are not configured, log the email instead
            logger.info(f"[SIMULATED EMAIL] To: {to_email}, Subject: {subject}, Body: {body[:100]}...")
            if attachments:
                logger.info(f"[SIMULATED EMAIL] Attachments: {attachments}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_sms(to_phone, message):
    """
    Send an SMS message
    
    Args:
        to_phone (str): Recipient phone number
        message (str): SMS message content
    
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    try:
        # In a real implementation, we would use Twilio or another SMS service
        # For this demo, we'll just log the message
        
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER:
            # If this were a real implementation, we would use the Twilio SDK
            # client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message,
            #     from_=TWILIO_PHONE_NUMBER,
            #     to=to_phone
            # )
            # logger.info(f"SMS sent to {to_phone}: {message.sid}")
            
            # For now, just log it
            logger.info(f"[TWILIO SMS] From: {TWILIO_PHONE_NUMBER}, To: {to_phone}, Message: {message}")
            return True
        else:
            # If Twilio settings are not configured, log the SMS instead
            logger.info(f"[SIMULATED SMS] To: {to_phone}, Message: {message}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        return False

def send_appointment_confirmation(patient_email, patient_phone, appointment_details):
    """
    Send appointment confirmation via email and SMS
    
    Args:
        patient_email (str): Patient's email address
        patient_phone (str): Patient's phone number
        appointment_details (dict): Dictionary with appointment details
    
    Returns:
        tuple: (email_success, sms_success)
    """
    # Format appointment date and time
    appointment_date = appointment_details.get('appointment_date')
    appointment_time = appointment_details.get('appointment_time')
    doctor_name = appointment_details.get('doctor_name')
    
    # Email confirmation
    subject = "Your Medical Appointment Confirmation"
    email_body = f"""
    <html>
    <body>
        <h2>Appointment Confirmation</h2>
        <p>Dear {appointment_details.get('patient_name')},</p>
        <p>Your appointment has been scheduled successfully:</p>
        <ul>
            <li><strong>Date:</strong> {appointment_date}</li>
            <li><strong>Time:</strong> {appointment_time}</li>
            <li><strong>Doctor:</strong> {doctor_name}</li>
            <li><strong>Location:</strong> {appointment_details.get('location', 'Main Clinic')}</li>
        </ul>
        <p>Please arrive 15 minutes before your scheduled appointment time.</p>
        <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
        <p>Thank you for choosing our medical practice.</p>
    </body>
    </html>
    """
    
    # SMS confirmation
    sms_message = f"Appointment confirmed with Dr. {doctor_name} on {appointment_date} at {appointment_time}. Reply Y to confirm or call to reschedule."
    
    # Send notifications
    email_success = send_email(patient_email, subject, email_body)
    sms_success = send_sms(patient_phone, sms_message)
    
    return (email_success, sms_success)

def send_appointment_reminder(patient_email, patient_phone, appointment_details, reminder_type):
    """
    Send appointment reminder via email and SMS
    
    Args:
        patient_email (str): Patient's email address
        patient_phone (str): Patient's phone number
        appointment_details (dict): Dictionary with appointment details
        reminder_type (str): Type of reminder (e.g., '7-day', '3-day', '1-day')
    
    Returns:
        tuple: (email_success, sms_success)
    """
    # Format appointment date and time
    appointment_date = appointment_details.get('appointment_date')
    appointment_time = appointment_details.get('appointment_time')
    doctor_name = appointment_details.get('doctor_name')
    patient_name = appointment_details.get('patient_name')
    
    # Determine reminder message based on type
    if reminder_type == '7-day':
        # First reminder - just a simple reminder
        subject = "Upcoming Appointment Reminder"
        email_body = f"""
        <html>
        <body>
            <h2>Appointment Reminder</h2>
            <p>Dear {patient_name},</p>
            <p>This is a friendly reminder about your upcoming appointment:</p>
            <ul>
                <li><strong>Date:</strong> {appointment_date}</li>
                <li><strong>Time:</strong> {appointment_time}</li>
                <li><strong>Doctor:</strong> {doctor_name}</li>
                <li><strong>Location:</strong> {appointment_details.get('location', 'Main Clinic')}</li>
            </ul>
            <p>Please arrive 15 minutes before your scheduled appointment time.</p>
            <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
            <p>Thank you for choosing our medical practice.</p>
        </body>
        </html>
        """
        
        sms_message = f"Reminder: You have an appointment with Dr. {doctor_name} on {appointment_date} at {appointment_time}. Reply Y to confirm or call to reschedule."
    
    elif reminder_type == '3-day':
        # Second reminder - ask about forms
        subject = "Important: Appointment Forms Reminder"
        email_body = f"""
        <html>
        <body>
            <h2>Appointment Reminder</h2>
            <p>Dear {patient_name},</p>
            <p>Your appointment is coming up soon:</p>
            <ul>
                <li><strong>Date:</strong> {appointment_date}</li>
                <li><strong>Time:</strong> {appointment_time}</li>
                <li><strong>Doctor:</strong> {doctor_name}</li>
                <li><strong>Location:</strong> {appointment_details.get('location', 'Main Clinic')}</li>
            </ul>
            <p><strong>Have you completed your intake forms?</strong> If not, please complete them before your appointment to save time.</p>
            <p><strong>Is your appointment still confirmed?</strong> Please reply to confirm or call us to reschedule.</p>
            <p>Thank you for choosing our medical practice.</p>
        </body>
        </html>
        """
        
        sms_message = f"Reminder: Appointment with Dr. {doctor_name} on {appointment_date} at {appointment_time}. Have you completed your forms? Is your appointment confirmed? Reply Y to confirm or call to reschedule."
    
    elif reminder_type == '1-day':
        # Final reminder - ask about forms and confirmation
        subject = "FINAL REMINDER: Your Appointment Tomorrow"
        email_body = f"""
        <html>
        <body>
            <h2>Final Appointment Reminder</h2>
            <p>Dear {patient_name},</p>
            <p>This is your final reminder about your appointment tomorrow:</p>
            <ul>
                <li><strong>Date:</strong> {appointment_date}</li>
                <li><strong>Time:</strong> {appointment_time}</li>
                <li><strong>Doctor:</strong> {doctor_name}</li>
                <li><strong>Location:</strong> {appointment_details.get('location', 'Main Clinic')}</li>
            </ul>
            <p><strong>Important:</strong></p>
            <ol>
                <li>Have you completed your intake forms? If not, please do so immediately.</li>
                <li>Is your appointment confirmed? If you need to cancel, please let us know immediately.</li>
                <li>If you need to cancel, please provide a reason so we can better assist you.</li>
            </ol>
            <p>Please arrive 15 minutes before your scheduled appointment time.</p>
            <p>Thank you for choosing our medical practice.</p>
        </body>
        </html>
        """
        
        sms_message = f"FINAL REMINDER: Appointment tomorrow with Dr. {doctor_name} at {appointment_time}. Have you completed your forms? Is your appointment confirmed? If you need to cancel, please provide a reason. Reply Y to confirm."
    
    else:
        # Generic reminder
        subject = "Appointment Reminder"
        email_body = f"""
        <html>
        <body>
            <h2>Appointment Reminder</h2>
            <p>Dear {patient_name},</p>
            <p>This is a reminder about your upcoming appointment:</p>
            <ul>
                <li><strong>Date:</strong> {appointment_date}</li>
                <li><strong>Time:</strong> {appointment_time}</li>
                <li><strong>Doctor:</strong> {doctor_name}</li>
                <li><strong>Location:</strong> {appointment_details.get('location', 'Main Clinic')}</li>
            </ul>
            <p>Please arrive 15 minutes before your scheduled appointment time.</p>
            <p>Thank you for choosing our medical practice.</p>
        </body>
        </html>
        """
        
        sms_message = f"Reminder: You have an appointment with Dr. {doctor_name} on {appointment_date} at {appointment_time}. Reply Y to confirm or call to reschedule."
    
    # Send notifications
    email_success = send_email(patient_email, subject, email_body)
    sms_success = send_sms(patient_phone, sms_message)
    
    return (email_success, sms_success)

def send_intake_forms(patient_email, patient_name, form_files):
    """
    Send intake forms to patient via email
    
    Args:
        patient_email (str): Patient's email address
        patient_name (str): Patient's name
        form_files (list): List of form file paths to attach
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Important: Your Medical Intake Forms"
    email_body = f"""
    <html>
    <body>
        <h2>Medical Intake Forms</h2>
        <p>Dear {patient_name},</p>
        <p>Please find attached the intake forms for your upcoming appointment.</p>
        <p><strong>Instructions:</strong></p>
        <ol>
            <li>Please complete all forms prior to your appointment.</li>
            <li>Bring the completed forms with you or email them back to us.</li>
            <li>If you have any questions about the forms, please contact our office.</li>
        </ol>
        <p>Thank you for choosing our medical practice.</p>
    </body>
    </html>
    """
    
    return send_email(patient_email, subject, email_body, attachments=form_files)

def export_appointment_to_excel(appointment_details, output_path=None):
    """
    Export appointment details to Excel for admin review
    
    Args:
        appointment_details (dict): Dictionary with appointment details
        output_path (str, optional): Path to save the Excel file
    
    Returns:
        str: Path to the saved Excel file
    """
    # Convert appointment details to DataFrame
    df = pd.DataFrame([appointment_details])
    
    # Generate output path if not provided
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'exports')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"appointment_{timestamp}.xlsx")
    
    # Export to Excel
    df.to_excel(output_path, index=False)
    logger.info(f"Exported appointment details to {output_path}")
    
    return output_path