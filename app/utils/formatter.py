# File: app/utils/formatter.py
import phonenumbers

def standardize_phone_number(raw_phone: str, default_region: str = "ID") -> str:
    """
    Parses and standardizes raw phone numbers into the international E.164 format.
    Prevents database inconsistencies and ensures third-party API (WhatsApp/SMS) compatibility.
    """
    try:
        # Default region "ID" menganggap input tanpa awalan negara adalah nomor Indonesia
        parsed_number = phonenumbers.parse(raw_phone, default_region)
        
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError(f"The number '{raw_phone}' is not a valid phone number for region {default_region}.")
            
        # Format ke standar E.164 (contoh: +6281234567890)
        standardized_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return standardized_number
        
    except phonenumbers.NumberParseException as e:
        raise ValueError(f"Phone number parsing encountered a critical error: {str(e)}")