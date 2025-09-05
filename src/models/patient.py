from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Patient:
    """Patient data model"""
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    date_of_birth: str = ""  # Format: YYYY-MM-DD
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get the patient's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> Optional[int]:
        """Calculate the patient's age based on date of birth"""
        if not self.date_of_birth:
            return None
        
        try:
            dob = datetime.strptime(self.date_of_birth, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        except ValueError:
            return None
    
    def to_dict(self) -> dict:
        """Convert patient to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Patient':
        """Create a Patient instance from a dictionary"""
        return cls(
            id=data.get('id'),
            first_name=data.get('first_name', ""),
            last_name=data.get('last_name', ""),
            date_of_birth=data.get('date_of_birth', ""),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class Insurance:
    """Insurance data model"""
    id: Optional[int] = None
    patient_id: int = 0
    carrier: str = ""
    member_id: str = ""
    group_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert insurance to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'carrier': self.carrier,
            'member_id': self.member_id,
            'group_id': self.group_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Insurance':
        """Create an Insurance instance from a dictionary"""
        return cls(
            id=data.get('id'),
            patient_id=data.get('patient_id', 0),
            carrier=data.get('carrier', ""),
            member_id=data.get('member_id', ""),
            group_id=data.get('group_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )