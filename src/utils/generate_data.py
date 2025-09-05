import os
import random
import logging
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

from src.models.patient import Patient
from src.models.appointment import Doctor
from src.utils.database import (
    initialize_database, 
    create_patient, 
    create_doctor,
    add_doctor_availability
)
from src.utils.forms import create_sample_forms

logger = logging.getLogger(__name__)

# Helper functions for generating synthetic data
def generate_random_name() -> tuple:
    """Generate a random first and last name"""
    first_names = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"
    ]
    
    return random.choice(first_names), random.choice(last_names)

def generate_random_date(start_year=1940, end_year=2000) -> str:
    """Generate a random date of birth"""
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Using 28 to avoid invalid dates
    
    return f"{year}-{month:02d}-{day:02d}"

def generate_random_email(first_name: str, last_name: str) -> str:
    """Generate a random email based on name"""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]
    return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"

def generate_random_phone() -> str:
    """Generate a random phone number"""
    return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def generate_random_address() -> str:
    """Generate a random address"""
    street_numbers = list(range(100, 10000))
    street_names = ["Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington", "Lake", "Hill"]
    street_types = ["St", "Ave", "Blvd", "Rd", "Ln", "Dr", "Way", "Pl", "Ct"]
    cities = ["Springfield", "Franklin", "Greenville", "Bristol", "Clinton", "Salem", "Madison", "Georgetown", "Arlington"]
    states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
    
    street_number = random.choice(street_numbers)
    street_name = random.choice(street_names)
    street_type = random.choice(street_types)
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = random.randint(10000, 99999)
    
    return f"{street_number} {street_name} {street_type}, {city}, {state} {zip_code}"

def generate_random_insurance() -> Dict[str, str]:
    """Generate random insurance information"""
    carriers = ["Blue Cross", "Aetna", "UnitedHealthcare", "Cigna", "Humana", "Kaiser", "Medicare", "Medicaid"]
    
    carrier = random.choice(carriers)
    member_id = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(10000000, 99999999)}"
    group_id = f"G{random.randint(10000, 99999)}"
    
    return {
        "carrier": carrier,
        "member_id": member_id,
        "group_id": group_id
    }

def generate_synthetic_patients(num_patients: int) -> List[Patient]:
    """Generate a list of synthetic patients"""
    patients = []
    
    for _ in range(num_patients):
        first_name, last_name = generate_random_name()
        date_of_birth = generate_random_date()
        email = generate_random_email(first_name, last_name)
        phone = generate_random_phone()
        address = generate_random_address()
        
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
            address=address
        )
        
        patients.append(patient)
    
    return patients

def generate_synthetic_doctors() -> List[Doctor]:
    """Generate a list of synthetic doctors"""
    specialties = [
        "Family Medicine", "Internal Medicine", "Pediatrics", "Cardiology", 
        "Dermatology", "Neurology", "Orthopedics", "Psychiatry", "Obstetrics"
    ]
    
    doctors = []
    
    # Generate 5 doctors with different specialties
    for i in range(5):
        first_name, last_name = generate_random_name()
        specialty = specialties[i % len(specialties)]
        email = f"dr.{last_name.lower()}@clinic.com"
        phone = generate_random_phone()
        
        doctor = Doctor(
            first_name=first_name,
            last_name=last_name,
            specialty=specialty,
            email=email,
            phone=phone
        )
        
        doctors.append(doctor)
    
    return doctors

def generate_doctor_schedule(doctor_id: int, start_date: datetime.date, num_days: int) -> None:
    """Generate a schedule for a doctor for a number of days"""
    # Working hours: 9 AM to 5 PM
    working_hours = list(range(9, 17))  # 9 AM to 4 PM (last appointment starts at 4 PM)
    
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        
        # Skip weekends
        if current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            continue
        
        # Generate available slots
        available_slots = []
        for hour in working_hours:
            # 50% chance of availability for each hour
            if random.random() > 0.5:
                available_slots.append(f"{hour:02d}:00")
                # Add 30-minute slots if it's not the last hour
                if hour < 16:  # Don't add 4:30 PM
                    available_slots.append(f"{hour:02d}:30")
        
        # Add the available slots to the database
        if available_slots:
            add_doctor_availability(doctor_id, current_date.strftime("%Y-%m-%d"), available_slots)

def export_patients_to_csv(patients: List[Patient], output_path: str = None) -> str:
    """Export patients to a CSV file"""
    if output_path is None:
        base_dir = Path(__file__).parent.parent.parent
        output_path = base_dir / 'data' / 'patients.csv'
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert patients to a list of dictionaries
    patient_dicts = [patient.to_dict() for patient in patients]
    
    # Create a DataFrame and export to CSV
    df = pd.DataFrame(patient_dicts)
    df.to_csv(output_path, index=False)
    
    logger.info(f"Exported {len(patients)} patients to {output_path}")
    
    return output_path

def generate_synthetic_data(num_patients: int = 50, num_days: int = 30) -> None:
    """Generate all synthetic data for the application"""
    # Initialize the database
    initialize_database()
    
    # Generate and save doctors
    doctors = generate_synthetic_doctors()
    doctor_ids = []
    for doctor in doctors:
        doctor_id = create_doctor(doctor)
        if doctor_id:
            doctor_ids.append(doctor_id)
    
    # Generate and save patients
    patients = generate_synthetic_patients(num_patients)
    for patient in patients:
        create_patient(patient)
    
    # Export patients to CSV
    export_patients_to_csv(patients)
    
    # Generate doctor schedules
    start_date = datetime.now().date()
    for doctor_id in doctor_ids:
        generate_doctor_schedule(doctor_id, start_date, num_days)
    
    # Create sample forms
    create_sample_forms()
    
    logger.info(f"Generated synthetic data: {len(patients)} patients, {len(doctors)} doctors, {num_days} days of schedules")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_synthetic_data()