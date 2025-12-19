import streamlit as st
import asyncio
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from backend import HealthcareBackend
from ai_engine import ClaudeAIEngine
from validators import (
    validate_name,
    validate_phone,
    validate_email,
    validate_age,
    validate_gender,
    validate_date,
    validate_time,
    validate_appointment_data,
    sanitize_input,
    normalize_phone,
    normalize_email,
    format_name
)
from config import *

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "backend" not in st.session_state:
        st.session_state.backend = HealthcareBackend()
    
    if "ai_engine" not in st.session_state:
        st.session_state.ai_engine = ClaudeAIEngine()
    
    if "role" not in st.session_state:
        st.session_state.role = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": GREETING_MESSAGE
        }]
    
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = {
            "current_intent": None,
            "collected_data": {},
            "current_step": None,
            "waiting_for": None
        }
    
    if "user_info" not in st.session_state:
        st.session_state.user_info = {}

    if "voice_mode" not in st.session_state:
        st.session_state.voice_mode = False
        
    if "draft_message" not in st.session_state:
        st.session_state.draft_message = ""
    
    if "last_audio_file" not in st.session_state:
        st.session_state.last_audio_file = None
        
    if "voice_key" not in st.session_state:
        st.session_state.voice_key = 0


def clear_session_state():
    st.session_state.conversation_state = {
        "current_intent": None,
        "collected_data": {},
        "current_step": None,
        "waiting_for": None
    }
    st.session_state.ai_engine.clear_history()


def reset_conversation():
    st.session_state.messages = [{
        "role": "assistant",
        "content": GREETING_MESSAGE
    }]
    clear_session_state()


def add_message(role: str, content: str):
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    })
    
    st.session_state.ai_engine.add_to_history(role, content)
    
    # Generate TTS if it's an assistant message and TTS is enabled
    if role == "assistant" and ENABLE_TTS and st.session_state.get("voice_mode", False):
        audio_file = asyncio.run(st.session_state.backend.text_to_speech(content))
        if audio_file:
            st.session_state.last_audio_file = audio_file


def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Play the latest audio if available
    if st.session_state.get("last_audio_file") and os.path.exists(st.session_state.last_audio_file):
        st.audio(st.session_state.last_audio_file, format="audio/mp3", autoplay=True)


def process_user_input(user_input: str):
    user_input = sanitize_input(user_input)
    
    if not user_input.strip():
        return
    
    add_message("user", user_input)
    
    if user_input.lower() in ["cancel", "restart", "reset", "start over"]:
        reset_conversation()
        st.rerun()
        return
    
    if user_input.lower() in ["help", "?"]:
        help_message = """I can help you with:
        
- **Book Appointment** - Say "I want to book an appointment"
- **View Appointments** - Say "Show my appointments"
- **Cancel Appointment** - Say "I want to cancel"
- **Report Symptoms** - Say "I'm not feeling well"
- **Hospital Info** - Ask about departments, doctors, timings

You can also type 'restart' to start over."""
        add_message("assistant", help_message)
        st.rerun()
        return
    
    with st.spinner("Thinking..."):
        conversation_history = st.session_state.ai_engine.get_history()
        
        result = st.session_state.ai_engine.process_message(
            user_input,
            conversation_history
        )
        
        if not result["success"]:
            add_message("assistant", ERROR_MESSAGES["api_error"])
            st.rerun()
            return
        
        response_data = result["data"]
        
        handle_ai_response(response_data)


def handle_ai_response(response_data: Dict):
    intent = response_data.get("intent", "general_query")
    response_text = response_data.get("response", "")
    collected_data = response_data.get("collected_data", {})
    next_action = response_data.get("next_action", "none")
    requires_validation = response_data.get("requires_validation", False)
    validation_field = response_data.get("validation_field")
    
    st.session_state.conversation_state["current_intent"] = intent
    st.session_state.conversation_state["collected_data"].update(
        {k: v for k, v in collected_data.items() if v is not None}
    )
    st.session_state.conversation_state["next_action"] = next_action
    
    if requires_validation and validation_field:
        collected_data["validation_field"] = validation_field
    
    if intent == "book_appointment":
        handle_appointment_booking(response_text, collected_data, next_action)
    
    elif intent == "view_appointment":
        handle_view_appointments(response_text, collected_data)
    
    elif intent == "cancel_appointment":
        handle_cancel_appointment(response_text, collected_data)
    
    elif intent == "symptom_report":
        handle_symptom_report(response_text, collected_data)
    
    else:
        handle_general_query(response_text)
    
    st.rerun()


def handle_appointment_booking(response_text: str, collected_data: Dict, next_action: str):
    validation_field = collected_data.get("validation_field")
    
    if validation_field == "patient_name":
        name = collected_data.get("patient_name", "")
        is_valid, error = validate_name(name)
        if not is_valid:
            add_message("assistant", f"❌ Invalid name: {error}\n\nPlease provide a valid name (letters only, at least 2 characters). What is your full name?")
            return
        else:
            st.session_state.conversation_state["collected_data"]["patient_name"] = name
            st.session_state.ai_engine.advance_step()
    
    elif validation_field == "phone":
        phone = collected_data.get("phone", "")
        is_valid, error = validate_phone(phone)
        if not is_valid:
            add_message("assistant", f"❌ Invalid phone number: {error}\n\nPlease provide a valid 10-digit phone number starting with 6, 7, 8, or 9.")
            return
        else:
            st.session_state.conversation_state["collected_data"]["phone"] = phone
            st.session_state.ai_engine.advance_step()
    
    elif validation_field == "email":
        email = collected_data.get("email", "")
        is_valid, error = validate_email(email)
        if not is_valid:
            add_message("assistant", f"❌ Invalid email: {error}\n\nPlease provide a valid email address (e.g., user@example.com).")
            return
        else:
            st.session_state.conversation_state["collected_data"]["email"] = email
            st.session_state.ai_engine.advance_step()
    
    elif validation_field == "age":
        age = collected_data.get("age", "")
        is_valid, error = validate_age(age)
        if not is_valid:
            add_message("assistant", f"❌ Invalid age: {error}\n\nPlease provide a valid age (1-120).")
            return
        else:
            st.session_state.conversation_state["collected_data"]["age"] = age
            st.session_state.ai_engine.advance_step()
    
    elif validation_field == "gender":
        gender = collected_data.get("gender", "")
        is_valid, error = validate_gender(gender)
        if not is_valid:
            add_message("assistant", f"❌ Invalid gender: {error}\n\nPlease enter Male, Female, or Other.")
            return
        else:
            st.session_state.conversation_state["collected_data"]["gender"] = gender
            st.session_state.ai_engine.advance_step()
    
    elif validation_field == "date":
        date = collected_data.get("date", "")
        is_valid, error = validate_date(date)
        if not is_valid:
            add_message("assistant", f"❌ Invalid date: {error}\n\nPlease provide date in YYYY-MM-DD format (e.g., 2025-12-25). Date must be in the future and within 30 days.")
            return
        else:
            st.session_state.conversation_state["collected_data"]["date"] = date
            st.session_state.ai_engine.advance_step()
    
    elif validation_field == "time":
        time_val = collected_data.get("time", "")
        is_valid, error = validate_time(time_val)
        if not is_valid:
            add_message("assistant", f"❌ Invalid time: {error}\n\nPlease provide time in HH:MM format (e.g., 14:30). Available hours: 09:00-17:30, slots at :00 and :30 only.")
            return
        else:
            st.session_state.conversation_state["collected_data"]["time"] = time_val
            st.session_state.ai_engine.advance_step()
    
    if next_action == "confirm_booking":
        data = st.session_state.conversation_state["collected_data"]
        
        is_valid, error_msg = validate_appointment_data(data)
        
        if not is_valid:
            add_message("assistant", f"❌ There's an issue: {error_msg}\n\nPlease type 'restart' to start over.")
            return
        
        if st.session_state.backend.db is None:
            add_message("assistant", "❌ Database connection error. Please check your MongoDB connection and try again.")
            clear_session_state()
            return
        
        available, error = st.session_state.backend.check_slot_availability(
            data["doctor_name"],
            data["date"],
            data["time"]
        )
        
        if not available:
            available_slots = st.session_state.backend.get_available_slots(
                data["doctor_name"],
                data["date"]
            )
            
            if available_slots:
                slots_text = ", ".join(available_slots[:5])
                add_message("assistant", 
                    f"❌ {error}\n\n**Available slots for {data['doctor_name']} on {data['date']}:**\n{slots_text}\n\nPlease choose a different time (HH:MM format):")
            else:
                add_message("assistant", 
                    f"❌ {error}\n\nNo available slots for this doctor on this date. Please type 'restart' and choose a different date or doctor.")
            
            st.session_state.ai_engine.current_step = "time"
            return
        
        payload = {
            "patient_name": format_name(data["patient_name"]),
            "phone": normalize_phone(data["phone"]),
            "email": normalize_email(data["email"]),
            "age": int(data["age"]),
            "gender": data["gender"],
            "department": data.get("department", "General Medicine"),
            "doctor_name": data["doctor_name"],
            "date": data["date"],
            "time": data["time"],
            "reason": data.get("reason", "General Consultation"),
            "address": data.get("address", "")
        }
        
        success, message = st.session_state.backend.book_appointment(payload)
        
        if success:
            summary = st.session_state.ai_engine.generate_appointment_summary(payload)
            confirmation = f"""✅ **APPOINTMENT BOOKED SUCCESSFULLY!**

{summary}

Your appointment has been confirmed and saved to our system.

📱 You'll receive confirmation at: {payload['email']}

Would you like to book another appointment? Type 'book appointment' or 'restart'."""
            add_message("assistant", confirmation)
            
            clear_session_state()
        else:
            add_message("assistant", f"❌ Failed to book appointment: {message}\n\nPlease type 'restart' to try again.")
            clear_session_state()
    else:
        if next_action in ["ask_doctor", "ask_date"]:
            if "department" in collected_data and collected_data["department"]:
                st.session_state.conversation_state["collected_data"]["department"] = collected_data["department"]
                st.session_state.ai_engine.advance_step()
            
            if "doctor_name" in collected_data and collected_data["doctor_name"]:
                st.session_state.conversation_state["collected_data"]["doctor_name"] = collected_data["doctor_name"]
                st.session_state.ai_engine.advance_step()
        
        if validation_field:
            collected_data_for_storage = {k: v for k, v in collected_data.items() if k != "validation_field"}
            st.session_state.conversation_state["collected_data"].update(collected_data_for_storage)
        
        add_message("assistant", response_text)


def handle_view_appointments(response_text: str, collected_data: Dict):
    validation_field = collected_data.get("validation_field")
    
    if validation_field == "phone":
        phone = collected_data.get("phone", "")
        is_valid, error = validate_phone(phone)
        if not is_valid:
            add_message("assistant", f"❌ Invalid phone number: {error}\n\nPlease provide a valid 10-digit phone number.")
            return
        
        normalized_phone = normalize_phone(phone)
        appointments = st.session_state.backend.get_appointments_by_phone(normalized_phone)
        
        if not appointments:
            add_message("assistant", "No appointments found for this phone number.")
            clear_session_state()
            return
        
        appt_text = "📋 **Your Appointments:**\n\n"
        for i, appt in enumerate(appointments, 1):
            appt_text += f"**{i}. Appointment Details:**\n"
            appt_text += f"   • Doctor: {appt['doctor_name']}\n"
            appt_text += f"   • Department: {appt.get('department', 'N/A')}\n"
            appt_text += f"   • Date: {appt['date']}\n"
            appt_text += f"   • Time: {appt['time']}\n"
            appt_text += f"   • Token: {appt.get('token', 'N/A')}\n"
            appt_text += f"   • Status: {appt['status']}\n\n"
        
        add_message("assistant", appt_text)
        clear_session_state()
    else:
        add_message("assistant", response_text)


def handle_cancel_appointment(response_text: str, collected_data: Dict):
    phone = collected_data.get("phone")
    appointment_id = collected_data.get("appointment_id")
    
    if not phone:
        add_message("assistant", "Please provide your phone number to cancel an appointment.")
        return
    
    is_valid, error = validate_phone(phone)
    if not is_valid:
        add_message("assistant", f"❌ Invalid phone number: {error}")
        return
    
    normalized_phone = normalize_phone(phone)
    
    if not appointment_id:
        appointments = st.session_state.backend.get_appointments_by_phone(normalized_phone)
        
        if not appointments:
            add_message("assistant", "No appointments found for this phone number.")
            return
        
        if len(appointments) == 1:
            appointment_id = appointments[0]["_id"]
        else:
            appt_list = "Which appointment would you like to cancel?\n\n"
            for i, appt in enumerate(appointments, 1):
                appt_list += f"{i}. {appt['doctor_name']} on {appt['date']} at {appt['time']}\n"
            
            add_message("assistant", appt_list + "\nPlease specify the appointment number.")
            return
    
    success, message = st.session_state.backend.cancel_appointment(
        appointment_id,
        normalized_phone
    )
    
    add_message("assistant", message)
    clear_session_state()


def handle_symptom_report(response_text: str, collected_data: Dict):
    symptoms = collected_data.get("symptoms")
    
    if not symptoms:
        add_message("assistant", "Please describe your symptoms in detail.")
        return
    
    patient_info = {
        "age": collected_data.get("age"),
        "gender": collected_data.get("gender")
    }
    
    analysis = st.session_state.ai_engine.analyze_symptoms(symptoms, patient_info)
    
    if analysis["success"]:
        data = analysis["data"]
        
        response = f"""Based on your symptoms, here's my assessment:

**Category:** {data['concern_category']}
**Recommended Department:** {data['recommended_department']}
**Urgency:** {data['urgency'].upper()}

**Advice:** {data['advice']}

⚠️ **Disclaimer:** {data['disclaimer']}

Would you like to book an appointment with the {data['recommended_department']} department?"""
        
        add_message("assistant", response)
    else:
        add_message("assistant", "I recommend consulting with our General Medicine department for proper evaluation.")


def handle_general_query(response_text: str):
    add_message("assistant", response_text)


def render_sidebar():
    with st.sidebar:
        st.title("🏥 Healthcare Assistant")
        
        st.divider()
        
        if st.button("🔄 New Conversation", use_container_width=True):
            reset_conversation()
            st.rerun()
        
        if st.button("❓ Help", use_container_width=True):
            help_text = """**Available Commands:**
            
- "restart" - Start new conversation
- "help" - Show this help
- "book appointment"
- "view appointments"
- "cancel appointment"
- "report symptoms"
"""
            st.info(help_text)
        
        st.divider()
        
        st.subheader("📊 Session Info")
        st.text(f"Session: {st.session_state.session_id[:8]}...")
        st.text(f"Messages: {len(st.session_state.messages)}")
        
        if st.session_state.conversation_state["current_intent"]:
            st.text(f"Intent: {st.session_state.conversation_state['current_intent']}")
        
        st.divider()
        
        st.subheader("🏥 Quick Info")
        hospital_info = st.session_state.backend.get_hospital_info()
        st.text(f"Hospital: {hospital_info.get('name', 'XYZ Hospital')}")
        st.text(f"Hours: {HOSPITAL_OPEN_HOUR}:00 AM - {HOSPITAL_CLOSE_HOUR}:00 PM")
        
        if st.button("🏥 View Departments", use_container_width=True):
            depts = st.session_state.backend.get_departments()
            st.write("**Departments:**")
            for dept in depts:
                st.write(f"• {dept}")
        
        st.divider()
        st.subheader("⚙️ Settings")
        st.session_state.voice_mode = st.toggle("🎤 Voice Mode", value=st.session_state.voice_mode)
        
        st.divider()
        st.subheader("🐞 Debug Info")
        st.json(st.session_state.conversation_state)
        st.write(f"Current Step: {st.session_state.ai_engine.current_step}")
        
        # Mock DB Debug
        if hasattr(st.session_state.backend.db, 'dump'):
            st.subheader("🗄️ Mock DB Content")
            st.json(st.session_state.backend.db.dump())


def main():
    init_session_state()
    
    st.title(f"{PAGE_ICON} AI Healthcare Receptionist")
    st.caption("Your 24/7 virtual healthcare assistant")
    
    render_sidebar()
    
    display_chat_messages()
    
    if st.session_state.voice_mode:
        # Dynamic key to allow clearing the input
        current_key = f"voice_input_{st.session_state.voice_key}"

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🎤 Record", use_container_width=True):
                with st.spinner("Recording..."):
                    audio_file = st.session_state.backend.record_audio()
                    if audio_file:
                        text = st.session_state.backend.transcribe_audio(audio_file)
                        if text:
                            st.session_state.draft_message = text
                            # Update the widget's session state value directly
                            st.session_state[current_key] = text
                            st.rerun()
        
        with col2:
            def submit_voice_input():
                # Get the value from the current widget key
                user_text = st.session_state.get(current_key)
                if user_text:
                    st.session_state.draft_message = "" # Clear draft
                    
                    # Increment key to force a new empty widget on next render
                    st.session_state.voice_key += 1
                    
                    process_user_input(user_text)

            st.text_input(
                "Your Message (Edit if needed - Press Enter to Send):", 
                value=st.session_state.draft_message, 
                key=current_key,
                on_change=submit_voice_input
            )
            
            if st.button("Send 🚀", use_container_width=True):
                # This button is a fallback if they don't press Enter
                if st.session_state.get(current_key):
                    submit_voice_input()
    else:
        user_input = st.chat_input("Type your message here...")
        if user_input:
            process_user_input(user_input)


if __name__ == "__main__":
    main()