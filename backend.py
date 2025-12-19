import os
import time
import json
import logging
import certifi
import whisper
import edge_tts
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pymongo import MongoClient, DESCENDING
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from typing import Dict, List, Optional, Tuple
from config import *
from mock_db import MockDatabase

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class HealthcareBackend:
    def __init__(self):
        self.cipher = self._init_cipher()
        self.whisper_model = None
        self.db = self._connect_db()
        self.kb_data = self._load_knowledge_base()
        
    def _init_cipher(self) -> Fernet:
        try:
            if ENCRYPTION_KEY:
                key = ENCRYPTION_KEY.encode()
            else:
                key_file = "secret.key"
                if os.path.exists(key_file):
                    with open(key_file, "rb") as f:
                        key = f.read()
                else:
                    key = Fernet.generate_key()
                    with open(key_file, "wb") as f:
                        f.write(key)
            
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize cipher: {e}")
            raise

    def _load_knowledge_base(self) -> Dict:
        try:
            kb_file = "Knowledge_Base.json"
            if not os.path.exists(kb_file):
                logger.warning(f"Knowledge base file not found: {kb_file}")
                return {
                    "hospitalDetails": {},
                    "departments": [],
                    "doctors": [],
                    "locations": {}
                }
            
            with open(kb_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            return {
                "hospitalDetails": {},
                "departments": [],
                "doctors": [],
                "locations": {}
            }

    def _connect_db(self) -> Optional[object]:
        try:
            client = MongoClient(
                MONGO_URI,
                tls=True,
                tlsCAFile=certifi.where(),
                retryWrites=True,
                connectTimeoutMS=10000,
                serverSelectionTimeoutMS=10000
            )
            
            client.admin.command("ping")
            logger.info("Successfully connected to MongoDB")
            
            db = client[DB_NAME]
            
            self._create_indexes(db)
            
            return db
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            logger.warning("Falling back to Mock Database (In-Memory)")
            return MockDatabase()
    
    def _create_indexes(self, db):
        try:
            db.appointments.create_index(
                [("phone", 1)],
                background=True
            )
            db.appointments.create_index(
                [("status", 1), ("created_at", -1)],
                background=True
            )
            db.appointments.create_index(
                [("doctor_name", 1), ("date", 1), ("time", 1)],
                background=True
            )
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")

    def encrypt(self, value: str) -> str:
        if not value:
            return ""
        # Skip encryption for Mock Database to simplify debugging
        if isinstance(self.db, MockDatabase):
            return value
            
        try:
            return self.cipher.encrypt(str(value).encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return value

    def decrypt(self, value: str) -> str:
        if not value:
            return ""
        # Skip decryption for Mock Database
        if isinstance(self.db, MockDatabase):
            return value

        try:
            return self.cipher.decrypt(value.encode()).decode()
        except Exception as e:
            logger.warning(f"Decryption failed, returning original: {e}")
            return value

    def get_departments(self) -> List[str]:
        try:
            return [dept["name"] for dept in self.kb_data.get("departments", [])]
        except Exception as e:
            logger.error(f"Failed to get departments: {e}")
            return DEFAULT_DEPARTMENTS

    def get_department_info(self, department_name: str) -> Optional[Dict]:
        try:
            for dept in self.kb_data.get("departments", []):
                if dept["name"].lower() == department_name.lower():
                    return dept
            return None
        except Exception as e:
            logger.error(f"Failed to get department info: {e}")
            return None

    def find_doctors(self, department: str = None, specialization: str = None) -> List[Dict]:
        try:
            doctors = self.kb_data.get("doctors", [])
            
            if department:
                doctors = [
                    doc for doc in doctors
                    if doc.get("specialization", "").lower() == department.lower()
                ]
            
            if specialization:
                doctors = [
                    doc for doc in doctors
                    if specialization.lower() in doc.get("specialization", "").lower()
                ]
            
            return doctors
            
        except Exception as e:
            logger.error(f"Failed to find doctors: {e}")
            return []

    def get_doctor_info(self, doctor_name: str) -> Optional[Dict]:
        try:
            for doc in self.kb_data.get("doctors", []):
                if doc["name"].lower() == doctor_name.lower():
                    return doc
            return None
        except Exception as e:
            logger.error(f"Failed to get doctor info: {e}")
            return None

    def check_slot_availability(
        self,
        doctor_name: str,
        date: str,
        time: str
    ) -> Tuple[bool, Optional[str]]:
        if self.db is None:
            return False, "Database connection error"
        
        try:
            existing = self.db.appointments.find_one({
                "doctor_name": doctor_name,
                "date": date,
                "time": time,
                "status": {"$ne": "Cancelled"}
            })
            
            if existing:
                return False, "This slot is already booked"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Failed to check availability: {e}")
            return False, "Error checking availability"

    def get_available_slots(
        self,
        doctor_name: str,
        date: str
    ) -> List[str]:
        try:
            doctor_info = self.get_doctor_info(doctor_name)
            if not doctor_info:
                return []
            
            consultation_hours = doctor_info.get("consultationHours", "9:00 AM - 5:00 PM")
            
            start_time_str = consultation_hours.split("-")[0].strip()
            end_time_str = consultation_hours.split("-")[1].strip()
            
            start_hour = self._parse_time_to_hour(start_time_str)
            end_hour = self._parse_time_to_hour(end_time_str)
            
            all_slots = []
            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:
                    slot_time = f"{hour:02d}:{minute:02d}"
                    all_slots.append(slot_time)
            
            if self.db is None:
                return all_slots
            
            booked_slots = []
            for appt in self.db.appointments.find({
                "doctor_name": doctor_name,
                "date": date,
                "status": {"$ne": "Cancelled"}
            }):
                booked_slots.append(appt.get("time"))
            
            available = [slot for slot in all_slots if slot not in booked_slots]
            
            return available
            
        except Exception as e:
            logger.error(f"Failed to get available slots: {e}")
            return []
    
    def _parse_time_to_hour(self, time_str: str) -> int:
        try:
            time_str = time_str.strip().upper()
            
            if "PM" in time_str:
                hour = int(time_str.split(":")[0])
                if hour != 12:
                    hour += 12
            else:
                hour = int(time_str.split(":")[0])
                if hour == 12:
                    hour = 0
            
            return hour
        except:
            return 9

    def book_appointment(self, payload: Dict) -> Tuple[bool, str]:
        if self.db is None:
            return False, ERROR_MESSAGES["db_error"]
        
        try:
            available, error_msg = self.check_slot_availability(
                payload.get("doctor_name"),
                payload.get("date"),
                payload.get("time")
            )
            
            if not available:
                return False, error_msg or "Slot not available"
            
            record = payload.copy()
            
            sensitive_fields = ["patient_name", "phone", "email", "address"]
            for field in sensitive_fields:
                if field in record and record[field]:
                    record[field] = self.encrypt(str(record[field]))
            
            record["status"] = "Scheduled"
            record["created_at"] = datetime.utcnow()
            record["updated_at"] = datetime.utcnow()
            
            token = self._generate_token()
            record["token"] = token
            
            result = self.db.appointments.insert_one(record)
            
            logger.info(f"Appointment booked: {result.inserted_id}")
            
            return True, str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to book appointment: {e}")
            return False, ERROR_MESSAGES["general_error"]

    def _generate_token(self) -> str:
        try:
            today = datetime.utcnow().strftime("%Y%m%d")
            
            if self.db:
                count = self.db.appointments.count_documents({
                    "created_at": {
                        "$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)
                    }
                })
                return f"{today}{count + 1:03d}"
            else:
                return f"{today}{int(time.time()) % 1000:03d}"
        except:
            return f"{int(time.time())}"

    def get_appointments_by_phone(self, phone: str) -> List[Dict]:
        if self.db is None:
            return []
        
        try:
            encrypted_phone = self.encrypt(phone)
            
            results = []
            for appt in self.db.appointments.find({
                "phone": encrypted_phone,
                "status": {"$ne": "Cancelled"}
            }).sort("created_at", DESCENDING):
                
                appt_dict = {
                    "_id": str(appt["_id"]),
                    "patient_name": self.decrypt(appt.get("patient_name", "")),
                    "doctor_name": appt.get("doctor_name", ""),
                    "department": appt.get("department", ""),
                    "date": appt.get("date", ""),
                    "time": appt.get("time", ""),
                    "token": appt.get("token", ""),
                    "status": appt.get("status", ""),
                    "created_at": appt.get("created_at", "")
                }
                results.append(appt_dict)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get appointments: {e}")
            return []

    def cancel_appointment(self, appointment_id: str, phone: str) -> Tuple[bool, str]:
        if self.db is None:
            return False, ERROR_MESSAGES["db_error"]
        
        try:
            encrypted_phone = self.encrypt(phone)
            
            appt = self.db.appointments.find_one({
                "_id": ObjectId(appointment_id),
                "phone": encrypted_phone
            })
            
            if not appt:
                return False, "Appointment not found or phone number doesn't match"
            
            if appt.get("status") == "Cancelled":
                return False, "Appointment is already cancelled"
            
            result = self.db.appointments.update_one(
                {"_id": ObjectId(appointment_id)},
                {
                    "$set": {
                        "status": "Cancelled",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Appointment cancelled: {appointment_id}")
                return True, SUCCESS_MESSAGES["appointment_cancelled"]
            else:
                return False, "Failed to cancel appointment"
                
        except Exception as e:
            logger.error(f"Failed to cancel appointment: {e}")
            return False, ERROR_MESSAGES["general_error"]

    def save_conversation(
        self,
        session_id: str,
        conversation_data: Dict
    ) -> bool:
        if self.db is None:
            return False
        
        try:
            self.db.conversations.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "conversation_data": conversation_data,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False

    def load_conversation(self, session_id: str) -> Optional[Dict]:
        if self.db is None:
            return None
        
        try:
            result = self.db.conversations.find_one({"session_id": session_id})
            if result:
                return result.get("conversation_data")
            return None
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            return None

    def get_hospital_info(self) -> Dict:
        try:
            return self.kb_data.get("hospitalDetails", {
                "name": HOSPITAL_DEFAULT_NAME,
                "address": HOSPITAL_DEFAULT_ADDRESS,
                "contactNumbers": {
                    "generalInquiry": HOSPITAL_DEFAULT_PHONE
                }
            })
        except Exception as e:
            logger.error(f"Failed to get hospital info: {e}")
            return {}

    async def text_to_speech(self, text: str) -> Optional[str]:
        if not ENABLE_TTS:
            return None
        
        try:
            filename = f"{AUDIO_OUTPUT_PREFIX}{int(time.time())}.mp3"
            communicate = edge_tts.Communicate(text=text, voice=TTS_VOICE)
            await communicate.save(filename)
            logger.info(f"TTS audio saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None

    def record_audio(self) -> Optional[str]:
        if not ENABLE_VOICE_INPUT:
            return None
        
        try:
            logger.info("Recording audio...")
            audio_data = sd.rec(
                int(AUDIO_RECORD_DURATION * AUDIO_SAMPLE_RATE),
                samplerate=AUDIO_SAMPLE_RATE,
                channels=1,
                dtype='int16'
            )
            sd.wait()
            
            wav.write(AUDIO_INPUT_FILE, AUDIO_SAMPLE_RATE, audio_data)
            logger.info(f"Audio recorded: {AUDIO_INPUT_FILE}")
            return AUDIO_INPUT_FILE
        except Exception as e:
            logger.error(f"Audio recording failed: {e}")
            return None

    def transcribe_audio(self, audio_file: str = None) -> Optional[str]:
        if not ENABLE_VOICE_INPUT:
            return None
        
        try:
            if not audio_file:
                audio_file = AUDIO_INPUT_FILE
            
            if not os.path.exists(audio_file):
                logger.error(f"Audio file not found: {audio_file}")
                return None
            
            if self.whisper_model is None:
                logger.info("Loading Whisper model...")
                self.whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
            
            result = self.whisper_model.transcribe(audio_file)
            transcription = result["text"].strip()
            
            logger.info(f"Transcription: {transcription}")
            return transcription
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None