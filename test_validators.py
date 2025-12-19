import pytest
from validators_improved import (
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
    format_name,
    parse_date_flexible,
    parse_time_flexible
)
from datetime import datetime, timedelta


class TestNameValidation:
    
    def test_valid_names(self):
        assert validate_name("John Doe")[0] == True
        assert validate_name("Mary Jane")[0] == True
        assert validate_name("O'Brien")[0] == True
        assert validate_name("Jean-Pierre")[0] == True
    
    def test_invalid_names(self):
        assert validate_name("")[0] == False
        assert validate_name("A")[0] == False
        assert validate_name("John123")[0] == False
        assert validate_name("@#$%")[0] == False
    
    def test_name_edge_cases(self):
        assert validate_name("A" * 101)[0] == False
        assert validate_name("   ")[0] == False


class TestPhoneValidation:
    
    def test_valid_phones(self):
        assert validate_phone("9876543210")[0] == True
        assert validate_phone("8765432109")[0] == True
        assert validate_phone("7654321098")[0] == True
        assert validate_phone("6543210987")[0] == True
    
    def test_invalid_phones(self):
        assert validate_phone("123456789")[0] == False
        assert validate_phone("12345678901")[0] == False
        assert validate_phone("1234567890")[0] == False
        assert validate_phone("abcdefghij")[0] == False
    
    def test_phone_formatting(self):
        assert validate_phone("(987) 654-3210")[0] == True
        assert validate_phone("+91 9876543210")[0] == True
    
    def test_normalize_phone(self):
        assert normalize_phone("(987) 654-3210") == "9876543210"
        assert normalize_phone("+91-9876543210") == "919876543210"


class TestEmailValidation:
    
    def test_valid_emails(self):
        assert validate_email("user@example.com")[0] == True
        assert validate_email("test.user@example.co.in")[0] == True
        assert validate_email("user+tag@example.com")[0] == True
    
    def test_invalid_emails(self):
        assert validate_email("invalid")[0] == False
        assert validate_email("@example.com")[0] == False
        assert validate_email("user@")[0] == False
        assert validate_email("user @example.com")[0] == False
    
    def test_normalize_email(self):
        assert normalize_email("User@EXAMPLE.COM") == "user@example.com"
        assert normalize_email("  test@test.com  ") == "test@test.com"


class TestAgeValidation:
    
    def test_valid_ages(self):
        assert validate_age("25")[0] == True
        assert validate_age("1")[0] == True
        assert validate_age("120")[0] == True
    
    def test_invalid_ages(self):
        assert validate_age("0")[0] == False
        assert validate_age("-5")[0] == False
        assert validate_age("121")[0] == False
        assert validate_age("abc")[0] == False


class TestGenderValidation:
    
    def test_valid_genders(self):
        assert validate_gender("Male")[0] == True
        assert validate_gender("m")[0] == True
        assert validate_gender("Female")[0] == True
        assert validate_gender("f")[0] == True
        assert validate_gender("Other")[0] == True
    
    def test_invalid_genders(self):
        assert validate_gender("invalid")[0] == False
        assert validate_gender("")[0] == False


class TestDateValidation:
    
    def test_valid_dates(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert validate_date(tomorrow)[0] == True
        
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        assert validate_date(next_week)[0] == True
    
    def test_invalid_dates(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        assert validate_date(yesterday)[0] == False
        
        assert validate_date("2025-13-01")[0] == False
        assert validate_date("invalid-date")[0] == False
    
    def test_date_parsing(self):
        assert parse_date_flexible("2025-12-25") == "2025-12-25"
        assert parse_date_flexible("25-12-2025") == "2025-12-25"
        assert parse_date_flexible("25/12/2025") == "2025-12-25"


class TestTimeValidation:
    
    def test_valid_times(self):
        assert validate_time("09:00")[0] == True
        assert validate_time("14:30")[0] == True
        assert validate_time("17:00")[0] == True
    
    def test_invalid_times(self):
        assert validate_time("08:00")[0] == False
        assert validate_time("18:30")[0] == False
        assert validate_time("14:15")[0] == False
        assert validate_time("25:00")[0] == False
    
    def test_time_parsing(self):
        assert parse_time_flexible("14:30") == "14:30"
        assert parse_time_flexible("2:30 PM") == "14:30"
        assert parse_time_flexible("2:30PM") == "14:30"


class TestSanitization:
    
    def test_sanitize_input(self):
        assert sanitize_input("<script>alert('xss')</script>") == ""
        assert sanitize_input("javascript:alert('xss')") == "alert('xss')"
        assert sanitize_input("Normal text") == "Normal text"
        assert sanitize_input("  Trimmed  ") == "Trimmed"


class TestAppointmentDataValidation:
    
    def test_valid_appointment_data(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        data = {
            "patient_name": "John Doe",
            "phone": "9876543210",
            "email": "john@example.com",
            "age": "30",
            "gender": "Male",
            "department": "Cardiology",
            "doctor_name": "Dr. Sharma",
            "date": tomorrow,
            "time": "10:00"
        }
        assert validate_appointment_data(data)[0] == True
    
    def test_missing_required_field(self):
        data = {
            "patient_name": "John Doe",
            "phone": "9876543210"
        }
        assert validate_appointment_data(data)[0] == False
    
    def test_invalid_field_value(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        data = {
            "patient_name": "John123",
            "phone": "9876543210",
            "email": "john@example.com",
            "age": "30",
            "gender": "Male",
            "department": "Cardiology",
            "doctor_name": "Dr. Sharma",
            "date": tomorrow,
            "time": "10:00"
        }
        assert validate_appointment_data(data)[0] == False


class TestFormatting:
    
    def test_format_name(self):
        assert format_name("john doe") == "John Doe"
        assert format_name("MARY JANE") == "Mary Jane"
        assert format_name("jean-pierre") == "Jean-Pierre"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])