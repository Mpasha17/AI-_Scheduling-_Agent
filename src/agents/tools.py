from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import pandas as pd

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.models.patient import Patient, Insurance
from src.models.appointment import Doctor, Appointment, Reminder, Form
from src.utils.database import (
    get_patient_by_name_dob, 
    create_patient, 
    get_doctor_availability, 
    create_appointment,
    get_doctor_by_id,
    get_patient_by_id,
    create_insurance,
    update_appointment_status,
    create_form,
    export_appointment_to_excel
)
from src.utils.communication import (
    send_appointment_confirmation,
    send_intake_forms
)

# Input schemas for tools
class PatientLookupInput(BaseModel):
    first_name: str = Field(description="Patient's first name")
    last_name: str = Field(description="Patient's last name")
    date_of_birth: str = Field(description="Patient's date of birth in YYYY-MM-DD format")

class PatientRegistrationInput(BaseModel):
    first_name: str = Field(description="Patient's first name")
    last_name: str = Field(description="Patient's last name")
    date_of_birth: str = Field(description="Patient's date of birth in YYYY-MM-DD format")
    email: str = Field(description="Patient's email address")
    phone: str = Field(description="Patient's phone number")
    address: Optional[str] = Field(description="Patient's address", default=None)

class DoctorAvailabilityInput(BaseModel):
    doctor_id: int = Field(description="Doctor's ID")
    date: str = Field(description="Date to check availability in YYYY-MM-DD format")

class AppointmentSchedulingInput(BaseModel):
    patient_id: int = Field(description="Patient's ID")
    doctor_id: int = Field(description="Doctor's ID")
    appointment_date: str = Field(description="Appointment date in YYYY-MM-DD format")
    appointment_time: str = Field(description="Appointment time in HH:MM format")
    is_new_patient: bool = Field(description="Whether this is a new patient appointment")
    notes: Optional[str] = Field(description="Additional notes for the appointment", default=None)

class InsuranceCollectionInput(BaseModel):
    patient_id: int = Field(description="Patient's ID")
    carrier: str = Field(description="Insurance carrier name")
    member_id: str = Field(description="Insurance member ID")
    group_id: Optional[str] = Field(description="Insurance group ID", default=None)

class AppointmentConfirmationInput(BaseModel):
    appointment_id: int = Field(description="Appointment ID to confirm")

class FormDistributionInput(BaseModel):
    patient_id: int = Field(description="Patient's ID")
    appointment_id: int = Field(description="Appointment ID")

class AppointmentExportInput(BaseModel):
    appointment_id: int = Field(description="Appointment ID to export")

# Tool implementations
class PatientLookupTool(BaseTool):
    name: str = "patient_lookup"
    description: str = "Look up a patient by name and date of birth"
    args_schema = PatientLookupInput
    
    def _run(self, first_name: str, last_name: str, date_of_birth: str) -> str:
        patient = get_patient_by_name_dob(first_name, last_name, date_of_birth)
        
        if patient:
            return json.dumps({
                "found": True,
                "patient": patient.to_dict(),
                "message": f"Found patient record for {patient.full_name}"
            })
        else:
            return json.dumps({
                "found": False,
                "message": f"No patient record found for {first_name} {last_name} with DOB {date_of_birth}"
            })

class PatientRegistrationTool(BaseTool):
    name: str = "patient_registration"
    description: str = "Register a new patient"
    args_schema = PatientRegistrationInput
    
    def _run(
        self, 
        first_name: str, 
        last_name: str, 
        date_of_birth: str, 
        email: str, 
        phone: str, 
        address: Optional[str] = None
    ) -> str:
        # First check if patient already exists
        existing_patient = get_patient_by_name_dob(first_name, last_name, date_of_birth)
        
        if existing_patient:
            return json.dumps({
                "success": False,
                "message": f"Patient {first_name} {last_name} already exists in our system",
                "patient": existing_patient.to_dict()
            })
        
        # Create new patient
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
            address=address
        )
        
        created_patient = create_patient(patient)
        
        if created_patient:
            return json.dumps({
                "success": True,
                "message": f"Successfully registered patient {first_name} {last_name}",
                "patient": created_patient.to_dict()
            })
        else:
            return json.dumps({
                "success": False,
                "message": "Failed to register patient due to a database error"
            })

class DoctorAvailabilityTool(BaseTool):
    name: str = "doctor_availability"
    description: str = "Check a doctor's availability for a specific date"
    args_schema = DoctorAvailabilityInput
    
    def _run(self, doctor_id: int, date: str) -> str:
        doctor = get_doctor_by_id(doctor_id)
        if not doctor:
            return json.dumps({
                "success": False,
                "message": f"No doctor found with ID {doctor_id}"
            })
        
        availability = get_doctor_availability(doctor_id, date)
        
        if availability:
            return json.dumps({
                "success": True,
                "doctor": doctor.to_dict(),
                "date": date,
                "available_slots": availability
            })
        else:
            return json.dumps({
                "success": False,
                "message": f"No available slots for Dr. {doctor.last_name} on {date}"
            })

class AppointmentSchedulingTool(BaseTool):
    name: str = "schedule_appointment"
    description: str = "Schedule an appointment for a patient with a doctor"
    args_schema = AppointmentSchedulingInput
    
    def _run(
        self, 
        patient_id: int, 
        doctor_id: int, 
        appointment_date: str, 
        appointment_time: str, 
        is_new_patient: bool, 
        notes: Optional[str] = None
    ) -> str:
        # Verify patient exists
        patient = get_patient_by_id(patient_id)
        if not patient:
            return json.dumps({
                "success": False,
                "message": f"No patient found with ID {patient_id}"
            })
        
        # Verify doctor exists
        doctor = get_doctor_by_id(doctor_id)
        if not doctor:
            return json.dumps({
                "success": False,
                "message": f"No doctor found with ID {doctor_id}"
            })
        
        # Check if the slot is available
        availability = get_doctor_availability(doctor_id, appointment_date)
        if not availability or appointment_time not in availability:
            return json.dumps({
                "success": False,
                "message": f"The selected time slot {appointment_time} is not available"
            })
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            duration=60 if is_new_patient else 30,  # 60 min for new patients, 30 min for returning
            status="scheduled",
            notes=notes
        )
        
        created_appointment = create_appointment(appointment)
        
        if created_appointment:
            return json.dumps({
                "success": True,
                "message": f"Successfully scheduled appointment for {patient.full_name} with Dr. {doctor.last_name}",
                "appointment": created_appointment.to_dict()
            })
        else:
            return json.dumps({
                "success": False,
                "message": "Failed to schedule appointment due to a database error"
            })

class InsuranceCollectionTool(BaseTool):
    name: str = "collect_insurance"
    description: str = "Collect insurance information for a patient"
    args_schema = InsuranceCollectionInput
    
    def _run(self, patient_id: int, carrier: str, member_id: str, group_id: Optional[str] = None) -> str:
        # Verify patient exists
        patient = get_patient_by_id(patient_id)
        if not patient:
            return json.dumps({
                "success": False,
                "message": f"No patient found with ID {patient_id}"
            })
        
        # Create insurance record
        insurance = Insurance(
            patient_id=patient_id,
            carrier=carrier,
            member_id=member_id,
            group_id=group_id
        )
        
        created_insurance = create_insurance(insurance)
        
        if created_insurance:
            return json.dumps({
                "success": True,
                "message": f"Successfully collected insurance information for {patient.full_name}",
                "insurance": created_insurance.to_dict()
            })
        else:
            return json.dumps({
                "success": False,
                "message": "Failed to collect insurance information due to a database error"
            })

class AppointmentConfirmationTool(BaseTool):
    name: str = "confirm_appointment"
    description: str = "Confirm an appointment and send confirmation to the patient"
    args_schema = AppointmentConfirmationInput
    
    def _run(self, appointment_id: int) -> str:
        # Update appointment status
        updated = update_appointment_status(appointment_id, "confirmed")
        
        if not updated:
            return json.dumps({
                "success": False,
                "message": f"No appointment found with ID {appointment_id}"
            })
        
        # Send confirmation email (simulated)
        sent = send_appointment_confirmation(appointment_id)
        
        if sent:
            return json.dumps({
                "success": True,
                "message": f"Appointment {appointment_id} confirmed and confirmation sent to patient"
            })
        else:
            return json.dumps({
                "success": True,
                "message": f"Appointment {appointment_id} confirmed but failed to send confirmation"
            })

class FormDistributionTool(BaseTool):
    name: str = "send_intake_forms"
    description: str = "Send intake forms to a patient for an appointment"
    args_schema = FormDistributionInput
    
    def _run(self, patient_id: int, appointment_id: int) -> str:
        # Verify patient exists
        patient = get_patient_by_id(patient_id)
        if not patient:
            return json.dumps({
                "success": False,
                "message": f"No patient found with ID {patient_id}"
            })
        
        # Create form records
        form_types = ["patient_information", "medical_history", "insurance_verification"]
        created_forms = []
        
        for form_type in form_types:
            form = Form(
                patient_id=patient_id,
                form_type=form_type,
                status="pending"
            )
            created_form = create_form(form)
            if created_form:
                created_forms.append(created_form)
        
        # Send forms via email (simulated)
        sent = send_intake_forms(patient_id, [f.id for f in created_forms])
        
        if sent:
            return json.dumps({
                "success": True,
                "message": f"Successfully sent intake forms to {patient.full_name}",
                "forms": [f.to_dict() for f in created_forms]
            })
        else:
            return json.dumps({
                "success": False,
                "message": f"Failed to send intake forms to {patient.full_name}"
            })

class AppointmentExportTool(BaseTool):
    name: str = "export_appointment"
    description: str = "Export appointment details to Excel for admin review"
    args_schema = AppointmentExportInput
    
    def _run(self, appointment_id: int) -> str:
        # Export appointment to Excel
        excel_path = export_appointment_to_excel(appointment_id)
        
        if excel_path:
            return json.dumps({
                "success": True,
                "message": f"Successfully exported appointment {appointment_id} to Excel",
                "excel_path": excel_path
            })
        else:
            return json.dumps({
                "success": False,
                "message": f"Failed to export appointment {appointment_id} to Excel"
            })

# List of all tools
def get_scheduling_tools() -> List[BaseTool]:
    return [
        PatientLookupTool(),
        PatientRegistrationTool(),
        DoctorAvailabilityTool(),
        AppointmentSchedulingTool(),
        InsuranceCollectionTool(),
        AppointmentConfirmationTool(),
        FormDistributionTool(),
        AppointmentExportTool()
    ]