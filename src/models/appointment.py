from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Doctor:
    """Doctor data model"""
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    specialty: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get the doctor's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """Convert doctor to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'specialty': self.specialty,
            'email': self.email,
            'phone': self.phone
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Doctor':
        """Create a Doctor instance from a dictionary"""
        return cls(
            id=data.get('id'),
            first_name=data.get('first_name', ""),
            last_name=data.get('last_name', ""),
            specialty=data.get('specialty', ""),
            email=data.get('email'),
            phone=data.get('phone')
        )

@dataclass
class Appointment:
    """Appointment data model"""
    id: Optional[int] = None
    patient_id: int = 0
    doctor_id: int = 0
    appointment_date: str = ""  # Format: YYYY-MM-DD
    appointment_time: str = ""  # Format: HH:MM
    duration: int = 30  # Duration in minutes
    status: str = "scheduled"  # scheduled, confirmed, cancelled, completed
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @property
    def is_new_patient_appointment(self) -> bool:
        """Check if this is a new patient appointment based on duration"""
        return self.duration == 60
    
    @property
    def appointment_datetime(self) -> Optional[datetime]:
        """Get the appointment date and time as a datetime object"""
        if not self.appointment_date or not self.appointment_time:
            return None
        
        try:
            dt_str = f"{self.appointment_date} {self.appointment_time}"
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return None
    
    def to_dict(self) -> dict:
        """Convert appointment to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'duration': self.duration,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Appointment':
        """Create an Appointment instance from a dictionary"""
        return cls(
            id=data.get('id'),
            patient_id=data.get('patient_id', 0),
            doctor_id=data.get('doctor_id', 0),
            appointment_date=data.get('appointment_date', ""),
            appointment_time=data.get('appointment_time', ""),
            duration=data.get('duration', 30),
            status=data.get('status', "scheduled"),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class Reminder:
    """Reminder data model"""
    id: Optional[int] = None
    appointment_id: int = 0
    reminder_type: str = ""  # e.g., "7-day", "3-day", "1-day"
    scheduled_time: str = ""  # Format: YYYY-MM-DD HH:MM
    status: str = "pending"  # pending, sent, failed
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert reminder to dictionary"""
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'reminder_type': self.reminder_type,
            'scheduled_time': self.scheduled_time,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Reminder':
        """Create a Reminder instance from a dictionary"""
        return cls(
            id=data.get('id'),
            appointment_id=data.get('appointment_id', 0),
            reminder_type=data.get('reminder_type', ""),
            scheduled_time=data.get('scheduled_time', ""),
            status=data.get('status', "pending"),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class Form:
    """Form data model"""
    id: Optional[int] = None
    patient_id: int = 0
    form_type: str = ""  # e.g., "patient_information", "medical_history", "insurance"
    status: str = "pending"  # pending, sent, completed
    sent_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert form to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'form_type': self.form_type,
            'status': self.status,
            'sent_at': self.sent_at,
            'completed_at': self.completed_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Form':
        """Create a Form instance from a dictionary"""
        return cls(
            id=data.get('id'),
            patient_id=data.get('patient_id', 0),
            form_type=data.get('form_type', ""),
            status=data.get('status', "pending"),
            sent_at=data.get('sent_at'),
            completed_at=data.get('completed_at'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )