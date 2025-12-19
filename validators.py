import re
from datetime import datetime, timedelta
from typing import Tuple, Optional


def validate_name(value: str) -> Tuple[bool, str]:
    try:
        name = value.strip()
        
        if not name:
            return False, "Name cannot be empty"
        
        if len(name) < 2:
            return False, "Name must have at least 2 characters"
        
        if len(name) > 100:
            return False, "Name is too long"
        
        if any(char.isdigit() for char in name):
            return False, "Name cannot contain numbers"
        
        if not re.match(r"^[a-zA-Z\s.'-]+$", name):
            return False, "Name contains invalid characters"
        
        return True, ""
    except Exception as e:
        return False, f"Error validating name: {str(e)}"


def validate_phone(value: str) -> Tuple[bool, str]:
    try:
        digits = re.sub(r"\D", "", value)
        
        if len(digits) != 10:
            return False, "Phone number must be exactly 10 digits"
        
        if not digits.startswith(('6', '7', '8', '9')):
            return False, "Phone number must start with 6, 7, 8, or 9"
        
        return True, ""
    except Exception as e:
        return False, f"Error validating phone: {str(e)}"


def validate_email(value: str) -> Tuple[bool, str]:
    try:
        email = value.strip().lower()
        
        if not email:
            return False, "Email cannot be empty"
        
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        if not re.match(pattern, email):
            return False, "Invalid email format. Example: user@example.com"
        
        if len(email) > 254:
            return False, "Email is too long"
        
        local_part = email.split('@')[0]
        if len(local_part) > 64:
            return False, "Email local part is too long"
        
        return True, ""
    except Exception as e:
        return False, f"Error validating email: {str(e)}"


def validate_age(value: str) -> Tuple[bool, str]:
    try:
        age = int(value)
        
        if age <= 0:
            return False, "Age must be a positive number"
        
        if age > 120:
            return False, "Age must be 120 or less"
        
        return True, ""
    except ValueError:
        return False, "Age must be a valid number"
    except Exception as e:
        return False, f"Error validating age: {str(e)}"


def validate_gender(value: str) -> Tuple[bool, str]:
    try:
        gender = value.strip().lower()
        
        valid_genders = {
            "male": "Male",
            "m": "Male",
            "female": "Female",
            "f": "Female",
            "other": "Other",
            "o": "Other",
            "prefer not to say": "Other"
        }
        
        if gender not in valid_genders:
            return False, "Gender must be Male, Female, or Other"
        
        return True, ""
    except Exception as e:
        return False, f"Error validating gender: {str(e)}"


def validate_date(value: str, max_days_ahead: int = 30) -> Tuple[bool, str]:
    try:
        date_str = value.strip()
        
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format (e.g., 2025-12-25)"
        
        today = datetime.utcnow().date()
        
        if date_obj < today:
            return False, "Date cannot be in the past"
        
        max_date = today + timedelta(days=max_days_ahead)
        if date_obj > max_date:
            return False, f"Date cannot be more than {max_days_ahead} days in the future"
        
        if date_obj.weekday() == 6:
            return False, "Hospital is closed on Sundays"
        
        return True, ""
    except Exception as e:
        return False, f"Error validating date: {str(e)}"


def validate_time(value: str, start_hour: int = 9, end_hour: int = 18) -> Tuple[bool, str]:
    try:
        time_str = value.strip()
        
        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return False, "Time must be in HH:MM format (24-hour, e.g., 14:30)"
        
        if not (start_hour <= time_obj.hour < end_hour):
            return False, f"Time must be between {start_hour:02d}:00 and {end_hour-1:02d}:59"
        
        if time_obj.minute not in [0, 30]:
            return False, "Appointments are available only at :00 or :30 minutes"
        
        return True, ""
    except Exception as e:
        return False, f"Error validating time: {str(e)}"


def validate_address(value: str) -> Tuple[bool, str]:
    try:
        address = value.strip()
        
        if not address:
            return False, "Address cannot be empty"
        
        if len(address) < 5:
            return False, "Address is too short"
        
        if len(address) > 500:
            return False, "Address is too long"
        
        return True, ""
    except Exception as e:
        return False, f"Error validating address: {str(e)}"


def validate_appointment_data(data: dict) -> Tuple[bool, str]:
    required_fields = [
        "patient_name",
        "phone",
        "email",
        "age",
        "gender",
        "department",
        "doctor_name",
        "date",
        "time"
    ]
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    validators = {
        "patient_name": validate_name,
        "phone": validate_phone,
        "email": validate_email,
        "age": validate_age,
        "gender": validate_gender,
        "date": validate_date,
        "time": validate_time
    }
    
    for field, validator in validators.items():
        if field in data:
            is_valid, error = validator(str(data[field]))
            if not is_valid:
                return False, f"{field}: {error}"
    
    if "address" in data and data["address"]:
        is_valid, error = validate_address(data["address"])
        if not is_valid:
            return False, f"address: {error}"
    
    return True, ""


def sanitize_input(value: str) -> str:
    if not value:
        return ""
    
    value = value.strip()
    
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed"
    ]
    
    for pattern in dangerous_patterns:
        value = re.sub(pattern, "", value, flags=re.IGNORECASE)
    
    return value


def normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def format_name(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split())


def parse_date_flexible(date_str: str) -> Optional[str]:
    date_formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y"
    ]
    
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_str.strip(), fmt)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return None


def parse_time_flexible(time_str: str) -> Optional[str]:
    time_str = time_str.strip().upper()
    
    time_formats = [
        "%H:%M",
        "%I:%M %p",
        "%I:%M%p",
        "%I %p"
    ]
    
    for fmt in time_formats:
        try:
            time_obj = datetime.strptime(time_str, fmt)
            return time_obj.strftime("%H:%M")
        except ValueError:
            continue
    
    return None