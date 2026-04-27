import requests
from langchain.tools import tool
from config import JAVA_BACKEND_URL, INTERNAL_API_SECRET

HEADERS = {"X-Internal-Secret": INTERNAL_API_SECRET}

@tool
def get_specialties() -> str:
    """Get all active medical specialties available on the platform."""
    url = f"{JAVA_BACKEND_URL}/api/internal/ai/specialties"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return str(response.json())
    except Exception as e:
        return f"Error fetching specialties: {str(e)}"

@tool
def search_doctors(specialty_name: str = None) -> str:
    """
    Search for doctors on the platform.
    Args:
        specialty_name: Optional name of the specialty to filter by (e.g. 'Psychology', 'Cardiology').
    """
    url = f"{JAVA_BACKEND_URL}/api/internal/ai/doctors"
    params = {}
    try:
        if specialty_name:
            # First, fetch specialties to resolve the string name into an ID
            spec_url = f"{JAVA_BACKEND_URL}/api/internal/ai/specialties"
            specs_req = requests.get(spec_url, headers=HEADERS)
            specs_req.raise_for_status()
            for s in specs_req.json():
                if specialty_name.lower() in str(s.get("name", "")).lower() or specialty_name.lower() in str(s.get("nameAr", "")).lower():
                    params["specialtyId"] = s.get("id")
                    break
            
            if "specialtyId" not in params:
                return f"Could not find any specialty matching '{specialty_name}'. Call get_specialties() to see official names."

        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return str(response.json())
    except Exception as e:
        return f"Error fetching doctors: {str(e)}"

@tool
def get_doctor_details(doctor_id: str) -> str:
    """
    Get full profile details for a specific doctor.
    Args:
        doctor_id: The ID of the doctor to fetch.
    """
    url = f"{JAVA_BACKEND_URL}/api/internal/ai/doctor/{doctor_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return str(response.json())
    except Exception as e:
        return f"Error fetching doctor details: {str(e)}"

@tool
def get_faqs() -> str:
    """Get general Frequently Asked Questions about the platform, booking appointments, and operations."""
    url = f"{JAVA_BACKEND_URL}/api/internal/ai/faq"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return str(response.json())
    except Exception as e:
        return f"Error fetching FAQs: {str(e)}"

@tool
def get_doctor_availability(doctor_id: str) -> str:
    """
    Check the available appointment time slots for a specific doctor.
    Args:
        doctor_id: The numeric ID of the doctor.
    """
    url = f"{JAVA_BACKEND_URL}/api/internal/ai/doctor/{doctor_id}/timeslots"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return str(response.json())
    except Exception as e:
        return f"Error fetching doctor availability: {str(e)}"

# List of all tools to bind to the agent
all_tools = [get_specialties, search_doctors, get_doctor_details, get_faqs, get_doctor_availability]
