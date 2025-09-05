import sqlite3
import os
import pandas as pd
from datetime import datetime
import logging
from ..config import DATABASE_PATH
from ..models.patient import Patient

logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Create a connection to the SQLite database
    """
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """
    Create database tables if they don't exist
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create doctors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        email TEXT,
        phone TEXT
    )
    ''')
    
    # Create appointments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        duration INTEGER NOT NULL,
        status TEXT DEFAULT 'scheduled',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id),
        FOREIGN KEY (doctor_id) REFERENCES doctors (id)
    )
    ''')
    
    # Create insurance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insurance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        carrier TEXT NOT NULL,
        member_id TEXT NOT NULL,
        group_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )
    ''')
    
    # Create reminders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL,
        reminder_type TEXT NOT NULL,
        scheduled_time TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments (id)
    )
    ''')
    
    # Create forms table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS forms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        form_type TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        sent_at TEXT,
        completed_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def find_patient(first_name=None, last_name=None, date_of_birth=None, patient_id=None):
    """
    Find a patient in the database based on provided criteria
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM patients WHERE "
    conditions = []
    params = []
    
    if patient_id:
        conditions.append("id = ?")
        params.append(patient_id)
    if first_name:
        conditions.append("LOWER(first_name) = LOWER(?)")
        params.append(first_name)
    if last_name:
        conditions.append("LOWER(last_name) = LOWER(?)")
        params.append(last_name)
    if date_of_birth:
        conditions.append("date_of_birth = ?")
        params.append(date_of_birth)
    
    if not conditions:
        return None
    
    query += " AND ".join(conditions)
    cursor.execute(query, params)
    patient = cursor.fetchone()
    conn.close()
    
    return dict(patient) if patient else None

def create_patient(first_name, last_name, date_of_birth, email=None, phone=None, address=None):
    """
    Create a new patient record
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO patients (first_name, last_name, date_of_birth, email, phone, address)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, date_of_birth, email, phone, address))
    
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Created new patient with ID: {patient_id}")
    return patient_id

def get_doctor_availability(doctor_id, date):
    """
    Get a doctor's availability for a specific date
    """
    # In a real implementation, this would query the doctor's schedule
    # For this demo, we'll use a simple approach with fixed hours
    
    # Get existing appointments for this doctor on this date
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT appointment_time, duration 
    FROM appointments 
    WHERE doctor_id = ? AND appointment_date = ? AND status != 'cancelled'
    ''', (doctor_id, date))
    
    booked_slots = cursor.fetchall()
    conn.close()
    
    # Define working hours (9 AM to 5 PM)
    working_hours = {
        'start': 9,  # 9 AM
        'end': 17    # 5 PM
    }
    
    # Generate all possible time slots (30-minute intervals)
    all_slots = []
    for hour in range(working_hours['start'], working_hours['end']):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            all_slots.append(time_str)
    
    # Remove booked slots
    available_slots = all_slots.copy()
    for appointment in booked_slots:
        time_str = appointment['appointment_time']
        duration = appointment['duration']
        
        # Convert time string to hour and minute
        hour, minute = map(int, time_str.split(':'))
        
        # Calculate how many 30-minute slots this appointment takes
        num_slots = duration // 30
        
        # Remove all affected slots
        for i in range(num_slots):
            slot_hour = hour + (minute + i * 30) // 60
            slot_minute = (minute + i * 30) % 60
            slot = f"{slot_hour:02d}:{slot_minute:02d}"
            
            if slot in available_slots:
                available_slots.remove(slot)
    
    return available_slots

def create_appointment(patient_id, doctor_id, appointment_date, appointment_time, duration, notes=None):
    """
    Create a new appointment
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, duration, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (patient_id, doctor_id, appointment_date, appointment_time, duration, notes))
    
    appointment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Created new appointment with ID: {appointment_id}")
    return appointment_id

def save_insurance_info(patient_id, carrier, member_id, group_id=None):
    """
    Save patient insurance information
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if insurance info already exists for this patient
    cursor.execute("SELECT id FROM insurance WHERE patient_id = ?", (patient_id,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        cursor.execute('''
        UPDATE insurance 
        SET carrier = ?, member_id = ?, group_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE patient_id = ?
        ''', (carrier, member_id, group_id, patient_id))
        insurance_id = existing['id']
    else:
        # Create new record
        cursor.execute('''
        INSERT INTO insurance (patient_id, carrier, member_id, group_id)
        VALUES (?, ?, ?, ?)
        ''', (patient_id, carrier, member_id, group_id))
        insurance_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    logger.info(f"Saved insurance info for patient ID: {patient_id}")
    return insurance_id

def schedule_reminders(appointment_id, reminder_days):
    """
    Schedule reminders for an appointment
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get appointment details
    cursor.execute("SELECT appointment_date FROM appointments WHERE id = ?", (appointment_id,))
    appointment = cursor.fetchone()
    
    if not appointment:
        conn.close()
        logger.error(f"Appointment with ID {appointment_id} not found")
        return False
    
    appointment_date = datetime.strptime(appointment['appointment_date'], "%Y-%m-%d")
    
    # Schedule reminders for each day in reminder_days
    reminder_ids = []
    for days in reminder_days:
        reminder_date = appointment_date - pd.Timedelta(days=days)
        reminder_time = "09:00"  # Send reminders at 9 AM
        scheduled_time = f"{reminder_date.strftime('%Y-%m-%d')} {reminder_time}"
        
        cursor.execute('''
        INSERT INTO reminders (appointment_id, reminder_type, scheduled_time)
        VALUES (?, ?, ?)
        ''', (appointment_id, f"{days}-day", scheduled_time))
        
        reminder_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Scheduled {len(reminder_ids)} reminders for appointment ID: {appointment_id}")
    return reminder_ids

def export_appointments_to_excel(output_path=None):
    """
    Export all appointments to an Excel file
    """
    conn = get_db_connection()
    
    # Query to get appointment details with patient and doctor information
    query = '''
    SELECT 
        a.id as appointment_id,
        a.appointment_date,
        a.appointment_time,
        a.duration,
        a.status,
        a.notes,
        p.first_name as patient_first_name,
        p.last_name as patient_last_name,
        p.date_of_birth as patient_dob,
        p.email as patient_email,
        p.phone as patient_phone,
        d.first_name as doctor_first_name,
        d.last_name as doctor_last_name,
        d.specialty as doctor_specialty,
        i.carrier as insurance_carrier,
        i.member_id as insurance_member_id,
        i.group_id as insurance_group_id
    FROM appointments a
    JOIN patients p ON a.patient_id = p.id
    JOIN doctors d ON a.doctor_id = d.id
    LEFT JOIN insurance i ON p.id = i.patient_id
    ORDER BY a.appointment_date, a.appointment_time
    '''
    
    # Read query results into a pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Generate output path if not provided
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"appointments_export_{timestamp}.xlsx"
    
    # Export to Excel
    df.to_excel(output_path, index=False)
    
    logger.info(f"Exported {len(df)} appointments to {output_path}")
    return output_path

def load_synthetic_data():
    """
    Load synthetic data into the database for testing purposes
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) as count FROM doctors")
    doctor_count = cursor.fetchone()['count']
    
    if doctor_count > 0:
        conn.close()
        logger.info("Synthetic data already loaded")
        return
    
    # Insert sample doctors
    doctors = [
        ('John', 'Smith', 'Family Medicine', 'john.smith@example.com', '555-123-4567'),
        ('Sarah', 'Johnson', 'Pediatrics', 'sarah.johnson@example.com', '555-234-5678'),
        ('Michael', 'Williams', 'Cardiology', 'michael.williams@example.com', '555-345-6789'),
        ('Emily', 'Brown', 'Dermatology', 'emily.brown@example.com', '555-456-7890'),
        ('David', 'Jones', 'Orthopedics', 'david.jones@example.com', '555-567-8901')
    ]
    
    cursor.executemany('''
    INSERT INTO doctors (first_name, last_name, specialty, email, phone)
    VALUES (?, ?, ?, ?, ?)
    ''', doctors)
    
    conn.commit()
    conn.close()
    
    logger.info("Loaded synthetic doctor data")
    
    # Note: Patient data will be generated separately in generate_data.py

def get_patient_by_name_dob(first_name, last_name, date_of_birth):
    """
    Find a patient by name and date of birth
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT * FROM patients 
    WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?) AND date_of_birth = ?
    """, (first_name, last_name, date_of_birth))
    
    patient = cursor.fetchone()
    conn.close()
    
    if patient:
        return dict(patient)
    return None

def get_doctor_by_id(doctor_id):
    """
    Get doctor information by ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
    doctor = cursor.fetchone()
    conn.close()
    
    if doctor:
        return dict(doctor)
    return None

def get_patient_by_id(patient_id):
    """
    Get patient information by ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    if patient:
        return dict(patient)
    return None

def create_insurance(patient_id, carrier, member_id, group_id=None):
    """
    Create insurance record for a patient
    """
    return save_insurance_info(patient_id, carrier, member_id, group_id)

def update_appointment_status(appointment_id, status, notes=None):
    """
    Update the status of an appointment
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if notes:
        cursor.execute("""
        UPDATE appointments 
        SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """, (status, notes, appointment_id))
    else:
        cursor.execute("""
        UPDATE appointments 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """, (status, appointment_id))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Updated appointment {appointment_id} status to {status}")
    return True

def create_form(patient_id, form_type):
    """
    Create a form record for a patient
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO forms (patient_id, form_type, sent_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (patient_id, form_type))
    
    form_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Created form {form_type} for patient {patient_id}")
    return form_id

def export_appointment_to_excel(appointment_id, output_path=None):
    """
    Export a specific appointment to Excel
    """
    conn = get_db_connection()
    
    # Query to get appointment details with patient and doctor information
    query = f"""
    SELECT 
        a.id as appointment_id,
        a.appointment_date,
        a.appointment_time,
        a.duration,
        a.status,
        a.notes,
        p.first_name as patient_first_name,
        p.last_name as patient_last_name,
        p.date_of_birth as patient_dob,
        p.email as patient_email,
        p.phone as patient_phone,
        d.first_name as doctor_first_name,
        d.last_name as doctor_last_name,
        d.specialty as doctor_specialty,
        i.carrier as insurance_carrier,
        i.member_id as insurance_member_id,
        i.group_id as insurance_group_id
    FROM appointments a
    JOIN patients p ON a.patient_id = p.id
    JOIN doctors d ON a.doctor_id = d.id
    LEFT JOIN insurance i ON p.id = i.patient_id
    WHERE a.id = {appointment_id}
    """
    
    # Read query results into a pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Generate output path if not provided
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"appointment_{appointment_id}_{timestamp}.xlsx"
    
    # Export to Excel
    df.to_excel(output_path, index=False)
    
    logger.info(f"Exported appointment {appointment_id} to {output_path}")
    return output_path

def get_patient_by_name_dob(first_name, last_name, date_of_birth):
    """
    Get a patient by name and date of birth
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT * FROM patients 
    WHERE first_name = ? AND last_name = ? AND date_of_birth = ?
    """
    
    cursor.execute(query, (first_name, last_name, date_of_birth))
    row = cursor.fetchone()
    
    if row:
        patient = Patient(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            date_of_birth=row['date_of_birth'],
            email=row['email'],
            phone=row['phone'],
            address=row['address']
        )
        conn.close()
        return patient
    
    conn.close()
    return None

# Initialize the database when this module is imported
initialize_database()