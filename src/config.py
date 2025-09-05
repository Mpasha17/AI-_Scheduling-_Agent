import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/medical_db.sqlite')

# Email Configuration
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')

# SMS Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Application Settings
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Appointment Settings
NEW_PATIENT_DURATION = 60  # minutes
RETURNING_PATIENT_DURATION = 30  # minutes

# Reminder Settings
REMINDER_DAYS = [7, 3, 1]  # Days before appointment to send reminders