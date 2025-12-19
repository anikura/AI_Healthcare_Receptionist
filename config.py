import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "healthcare_assistant")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in environment variables")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY not set in environment variables")

COLLECTION_APPOINTMENTS = "appointments"
COLLECTION_PATIENT_REPORTS = "patient_reports"
COLLECTION_HOSPITAL_INFO = "hospital_info"
COLLECTION_CONVERSATIONS = "conversations"

HOSPITAL_DEFAULT_NAME = os.getenv("HOSPITAL_NAME", "XYZ Hospital")
HOSPITAL_DEFAULT_ADDRESS = os.getenv("HOSPITAL_ADDRESS", "123 Health Street, New Delhi")
HOSPITAL_DEFAULT_PHONE = os.getenv("HOSPITAL_PHONE", "+91-1234567890")

HOSPITAL_OPEN_HOUR = int(os.getenv("HOSPITAL_OPEN_HOUR", 9))
HOSPITAL_CLOSE_HOUR = int(os.getenv("HOSPITAL_CLOSE_HOUR", 18))

MAX_BOOKING_DAYS_AHEAD = int(os.getenv("MAX_BOOKING_DAYS_AHEAD", 30))
APPOINTMENT_DURATION_MINUTES = int(os.getenv("APPOINTMENT_DURATION_MINUTES", 30))

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-JennyNeural")

ENABLE_VOICE_INPUT = os.getenv("ENABLE_VOICE_INPUT", "true").lower() == "true"
ENABLE_TTS = os.getenv("ENABLE_TTS", "true").lower() == "true"
ENABLE_AI_SUMMARY = os.getenv("ENABLE_AI_SUMMARY", "true").lower() == "true"
ENABLE_AVAILABILITY_CHECK = os.getenv("ENABLE_AVAILABILITY_CHECK", "true").lower() == "true"

USE_AWS_SECRETS = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

AUDIO_INPUT_FILE = os.getenv("AUDIO_INPUT_FILE", "input_audio.wav")
AUDIO_OUTPUT_PREFIX = os.getenv("AUDIO_OUTPUT_PREFIX", "response_")
AUDIO_RECORD_DURATION = int(os.getenv("AUDIO_RECORD_DURATION", 5))
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", 44100))

LOG_FILE = os.getenv("LOG_FILE", "healthcare_bot.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

PAGE_TITLE = os.getenv("PAGE_TITLE", "AI Healthcare Receptionist")
PAGE_ICON = os.getenv("PAGE_ICON", "🏥")

GREETING_MESSAGE = """Hello! I'm your AI Healthcare Assistant. I can help you with:

- **Book Appointments** - Schedule visits with our doctors
- **View Appointments** - Check your upcoming appointments
- **Cancel Appointments** - Cancel or reschedule bookings
- **Report Symptoms** - Get preliminary health guidance
- **General Queries** - Ask about departments, doctors, or hospital info

How can I assist you today?"""

DEFAULT_DEPARTMENTS = [
    "Cardiology",
    "Neurology",
    "Pediatrics",
    "Orthopedics",
    "Gynecology",
    "Dermatology",
    "Endocrinology",
    "ENT",
    "Gastroenterology",
    "General Medicine"
]

DEFAULT_DOCTORS = [
    "Dr. Verma",
    "Dr. Banerjee",
    "Dr. Roy",
    "Dr. Sharma",
    "Dr. Gupta"
]

MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", 10))
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", 30))

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

ERROR_MESSAGES = {
    "api_error": "I'm having trouble processing your request. Please try again.",
    "db_error": "Unable to connect to our database. Please try again later.",
    "validation_error": "The information provided doesn't seem correct. Please check and try again.",
    "timeout_error": "Your session has timed out. Please start over.",
    "general_error": "Something went wrong. Our team has been notified."
}

SUCCESS_MESSAGES = {
    "appointment_booked": "✅ Appointment booked successfully! You'll receive a confirmation email shortly.",
    "appointment_cancelled": "✅ Your appointment has been cancelled.",
    "information_updated": "✅ Information updated successfully."
}