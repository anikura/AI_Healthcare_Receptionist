import json
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeAIEngine:
    def __init__(self):
        self.conversation_history = []
        self.collected_info = {}
        self.current_step = None
        
    def _build_system_prompt(self) -> str:
        return ""

    def process_message(
        self,
        user_message: str,
        conversation_context: Optional[List[Dict]] = None
    ) -> Dict:
        try:
            user_message_lower = user_message.lower().strip()
            
            if not self.current_step:
                if any(word in user_message_lower for word in ["view", "show", "check", "my appointments", "see"]):
                    self.current_step = "view_phone"
                    return {
                        "success": True,
                        "data": {
                            "intent": "view_appointment",
                            "response": "I can help you view your appointments. Please provide your **phone number** (10 digits).",
                            "collected_data": {},
                            "next_action": "ask_phone",
                            "requires_validation": False
                        },
                        "raw_response": ""
                    }
                
                elif any(word in user_message_lower for word in ["cancel", "remove", "delete"]):
                    self.current_step = "cancel_phone"
                    return {
                        "success": True,
                        "data": {
                            "intent": "cancel_appointment",
                            "response": "I can help you cancel an appointment. Please provide your **phone number**.",
                            "collected_data": {},
                            "next_action": "ask_phone",
                            "requires_validation": False
                        },
                        "raw_response": ""
                    }

                elif any(word in user_message_lower for word in ["book", "appointment", "schedule", "booking"]):
                    self.current_step = "name"
                    return {
                        "success": True,
                        "data": {
                            "intent": "book_appointment",
                            "response": "I'd be happy to help you book an appointment. What is your **full name**?",
                            "collected_data": {},
                            "next_action": "ask_name",
                            "requires_validation": False
                        },
                        "raw_response": ""
                    }
                
                elif any(word in user_message_lower for word in ["symptom", "sick", "pain", "fever", "cough", "headache"]):
                    return {
                        "success": True,
                        "data": {
                            "intent": "symptom_report",
                            "response": "I understand you're not feeling well. Please describe your symptoms in detail.",
                            "collected_data": {"symptoms": user_message},
                            "next_action": "none",
                            "requires_validation": False
                        },
                        "raw_response": ""
                    }
                
                elif any(word in user_message_lower for word in ["doctor", "doctors", "department", "departments"]):
                    return {
                        "success": True,
                        "data": {
                            "intent": "general_query",
                            "response": "We have the following departments:\n• Cardiology\n• Neurology\n• Pediatrics\n• Orthopedics\n• Gynecology\n• Dermatology\n• ENT\n• General Medicine\n\nWould you like to book an appointment?",
                            "collected_data": {},
                            "next_action": "none",
                            "requires_validation": False
                        },
                        "raw_response": ""
                    }
                
                else:
                    return {
                        "success": True,
                        "data": {
                            "intent": "general_query",
                            "response": "Hello! I can help you with:\n\n• **Book an appointment** - Say 'book appointment'\n• **View appointments** - Say 'view appointments'\n• **Cancel appointment** - Say 'cancel appointment'\n• **Report symptoms** - Describe your symptoms\n\nWhat would you like to do?",
                            "collected_data": {},
                            "next_action": "none",
                            "requires_validation": False
                        },
                        "raw_response": ""
                    }
            
            else:
                return self._handle_booking_flow(user_message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {
                    "intent": "error",
                    "response": "I'm having trouble processing your request. Please try again.",
                    "collected_data": {},
                    "next_action": "none",
                    "requires_validation": False
                }
            }
    
    def _match_department(self, user_input: str) -> Optional[str]:
        dept_map = {
            "cardiology": "Cardiology",
            "cardio": "Cardiology",
            "heart": "Cardiology",
            "neurology": "Neurology",
            "neuro": "Neurology",
            "brain": "Neurology",
            "pediatrics": "Pediatrics",
            "pediatric": "Pediatrics",
            "child": "Pediatrics",
            "kids": "Pediatrics",
            "orthopedics": "Orthopedics",
            "ortho": "Orthopedics",
            "bone": "Orthopedics",
            "gynecology": "Gynecology",
            "gynae": "Gynecology",
            "women": "Gynecology",
            "dermatology": "Dermatology",
            "derma": "Dermatology",
            "skin": "Dermatology",
            "ent": "ENT",
            "ear": "ENT",
            "nose": "ENT",
            "throat": "ENT",
            "gastroenterology": "Gastroenterology",
            "gastro": "Gastroenterology",
            "stomach": "Gastroenterology",
            "general medicine": "General Medicine",
            "general": "General Medicine",
            "gp": "General Medicine"
        }
        
        user_lower = user_input.lower().strip()
        
        if user_lower in dept_map:
            return dept_map[user_lower]
        
        for key, value in dept_map.items():
            if key in user_lower or user_lower in key:
                return value
        
        return None
    
    def _match_doctor(self, user_input: str, available_doctors: list) -> Optional[str]:
        user_lower = user_input.lower().strip()
        
        for doctor in available_doctors:
            doctor_lower = doctor.lower()
            doctor_name_only = doctor_lower.replace("dr.", "").replace("dr ", "").strip()
            
            if user_lower == doctor_lower or user_lower == doctor_name_only:
                return doctor
            
            if doctor_name_only in user_lower or user_lower in doctor_name_only:
                return doctor
        
        return None
    
    def _handle_booking_flow(self, user_input: str) -> Dict:
        if self.current_step == "name":
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": f"Thank you. What is your **phone number**? (10 digits)",
                    "collected_data": {"patient_name": user_input.strip()},
                    "next_action": "ask_phone",
                    "requires_validation": True,
                    "validation_field": "patient_name"
                },
                "raw_response": ""
            }
        
        elif self.current_step == "phone":
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": "What is your **email address**?",
                    "collected_data": {"phone": user_input.strip()},
                    "next_action": "ask_email",
                    "requires_validation": True,
                    "validation_field": "phone"
                },
                "raw_response": ""
            }
        
        elif self.current_step == "email":
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": "What is your **age**?",
                    "collected_data": {"email": user_input.strip()},
                    "next_action": "ask_age",
                    "requires_validation": True,
                    "validation_field": "email"
                },
                "raw_response": ""
            }
        
        elif self.current_step == "age":
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": "What is your **gender**? (Male/Female/Other)",
                    "collected_data": {"age": user_input.strip()},
                    "next_action": "ask_gender",
                    "requires_validation": True,
                    "validation_field": "age"
                },
                "raw_response": ""
            }
        
        elif self.current_step == "gender":
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": "Which **department** would you like to visit?\n• Cardiology (heart)\n• Neurology (brain/nerves)\n• Pediatrics (children)\n• Orthopedics (bones/joints)\n• Gynecology (women's health)\n• Dermatology (skin)\n• ENT (ear/nose/throat)\n• General Medicine",
                    "collected_data": {"gender": user_input.strip()},
                    "next_action": "ask_department",
                    "requires_validation": True,
                    "validation_field": "gender"
                },
                "raw_response": ""
            }
        
        elif self.current_step == "department":
            dept_doctors = {
                "cardiology": ["Dr. Verma", "Dr. Banerjee"],
                "neurology": ["Dr. Sharma"],
                "pediatrics": ["Dr. Mehta", "Dr. Gupta"],
                "orthopedics": ["Dr. Roy"],
                "gynecology": ["Dr. Kapoor"],
                "dermatology": ["Dr. Singh"],
                "general medicine": ["Dr. Patel"],
                "ent": ["Dr. Nair"],
                "gastroenterology": ["Dr. Saxena"]
            }
            
            matched_dept = self._match_department(user_input)
            
            if not matched_dept:
                return {
                    "success": True,
                    "data": {
                        "intent": "book_appointment",
                        "response": f"❌ I couldn't find '{user_input}' in our departments.\n\nPlease choose from:\n• Cardiology (heart)\n• Neurology (brain)\n• Pediatrics (children)\n• Orthopedics (bones)\n• Gynecology (women)\n• Dermatology (skin)\n• ENT (ear/nose/throat)\n• General Medicine",
                        "collected_data": {},
                        "next_action": "ask_department",
                        "requires_validation": False
                    },
                    "raw_response": ""
                }
            
            doctors = dept_doctors.get(matched_dept.lower(), ["Dr. Patel"])
            doctors_list = "\n• ".join(doctors)
            
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": f"Available doctors in {matched_dept}:\n• {doctors_list}\n\nWhich **doctor** would you prefer?",
                    "collected_data": {"department": matched_dept},
                    "next_action": "ask_doctor",
                    "requires_validation": False
                },
                "raw_response": ""
            }
        
        elif self.current_step == "doctor":
            all_doctors = [
                "Dr. Verma", "Dr. Banerjee", "Dr. Sharma", "Dr. Mehta", 
                "Dr. Gupta", "Dr. Roy", "Dr. Kapoor", "Dr. Singh", 
                "Dr. Patel", "Dr. Nair", "Dr. Saxena"
            ]
            
            matched_doctor = self._match_doctor(user_input, all_doctors)
            
            if not matched_doctor:
                return {
                    "success": True,
                    "data": {
                        "intent": "book_appointment",
                        "response": f"❌ I couldn't find a doctor named '{user_input}'.\n\nPlease enter the doctor's name from the list above.",
                        "collected_data": {},
                        "next_action": "ask_doctor",
                        "requires_validation": False
                    },
                    "raw_response": ""
                }
            
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": "What **date** would you like? (Format: YYYY-MM-DD, e.g., 2025-12-25)",
                    "collected_data": {"doctor_name": matched_doctor},
                    "next_action": "ask_date",
                    "requires_validation": False
                },
                "raw_response": ""
            }
        
        elif self.current_step == "date":
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": "What **time** would you prefer? (Format: HH:MM, e.g., 14:30)\nAvailable slots: 09:00, 09:30, 10:00, 10:30, 11:00, 11:30, 14:00, 14:30, 15:00, 15:30, 16:00, 16:30",
                    "collected_data": {"date": user_input.strip()},
                    "next_action": "ask_time",
                    "requires_validation": True,
                    "validation_field": "date"
                },
                "raw_response": ""
            }
        
        elif self.current_step == "time":
            return {
                "success": True,
                "data": {
                    "intent": "book_appointment",
                    "response": "confirm_booking",
                    "collected_data": {"time": user_input.strip()},
                    "next_action": "confirm_booking",
                    "requires_validation": True,
                    "validation_field": "time"
                },
                "raw_response": ""
            }
        
        elif self.current_step == "view_phone":
            return {
                "success": True,
                "data": {
                    "intent": "view_appointment",
                    "response": "",
                    "collected_data": {"phone": user_input.strip()},
                    "next_action": "show_appointments",
                    "requires_validation": True,
                    "validation_field": "phone"
                },
                "raw_response": ""
            }
        
        elif self.current_step == "cancel_phone":
            return {
                "success": True,
                "data": {
                    "intent": "cancel_appointment",
                    "response": "",
                    "collected_data": {"phone": user_input.strip()},
                    "next_action": "cancel_appointment",
                    "requires_validation": True,
                    "validation_field": "phone"
                },
                "raw_response": ""
            }
        
        return {
            "success": True,
            "data": {
                "intent": "general_query",
                "response": "I didn't understand that. Please try again.",
                "collected_data": {},
                "next_action": "none",
                "requires_validation": False
            },
            "raw_response": ""
        }
    
    def advance_step(self):
        step_order = ["name", "phone", "email", "age", "gender", "department", "doctor", "date", "time"]
        if self.current_step in step_order:
            current_index = step_order.index(self.current_step)
            if current_index < len(step_order) - 1:
                self.current_step = step_order[current_index + 1]
            else:
                self.current_step = None
    
    def extract_appointment_info(
        self,
        conversation_history: List[Dict]
    ) -> Dict:
        return {
            "success": True,
            "data": self.collected_info
        }
    
    def analyze_symptoms(
        self,
        symptoms: str,
        patient_info: Optional[Dict] = None
    ) -> Dict:
        symptoms_lower = symptoms.lower()
        
        if any(word in symptoms_lower for word in ["heart", "chest", "cardiac"]):
            dept = "Cardiology"
        elif any(word in symptoms_lower for word in ["head", "brain", "nerve", "seizure"]):
            dept = "Neurology"
        elif any(word in symptoms_lower for word in ["child", "baby", "kid"]):
            dept = "Pediatrics"
        elif any(word in symptoms_lower for word in ["bone", "joint", "fracture", "sprain"]):
            dept = "Orthopedics"
        elif any(word in symptoms_lower for word in ["skin", "rash", "acne"]):
            dept = "Dermatology"
        else:
            dept = "General Medicine"
        
        return {
            "success": True,
            "data": {
                "concern_category": "General Health Concern",
                "recommended_department": dept,
                "urgency": "routine",
                "advice": "Please consult with a doctor for proper evaluation of your symptoms.",
                "disclaimer": "This is not a medical diagnosis. Please consult a doctor."
            }
        }
    
    def generate_appointment_summary(
        self,
        appointment_data: Dict
    ) -> str:
        return f"""Dear {appointment_data.get('patient_name', 'Patient')},

Your appointment has been confirmed!

📅 **Appointment Details:**
- Doctor: {appointment_data.get('doctor_name', 'N/A')}
- Department: {appointment_data.get('department', 'N/A')}
- Date: {appointment_data.get('date', 'N/A')}
- Time: {appointment_data.get('time', 'N/A')}

📞 If you need to reschedule, please call us or use this chatbot.

Thank you for choosing our hospital!"""
    
    def add_to_history(
        self,
        role: str,
        content: str
    ):
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def clear_history(self):
        self.conversation_history = []
        self.collected_info = {}
        self.current_step = None
    
    def get_history(self) -> List[Dict]:
        return self.conversation_history.copy()