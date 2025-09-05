import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def create_sample_forms():
    """Create sample form files for the application"""
    # Get the forms directory
    base_dir = Path(__file__).parent.parent.parent
    forms_dir = base_dir / 'data' / 'forms'
    
    # Create the directory if it doesn't exist
    forms_dir.mkdir(parents=True, exist_ok=True)
    
    # Define the sample forms
    sample_forms = {
        'patient_information.pdf': """
        PATIENT INFORMATION FORM
        
        Personal Information:
        Full Name: ____________________________
        Date of Birth: ________________________
        Address: _____________________________
        City, State, ZIP: _____________________
        Phone Number: ________________________
        Email: _______________________________
        
        Emergency Contact:
        Name: ________________________________
        Relationship: _________________________
        Phone Number: ________________________
        
        Primary Insurance:
        Insurance Company: ____________________
        Member ID: ___________________________
        Group Number: ________________________
        Policy Holder Name: __________________
        
        Secondary Insurance (if applicable):
        Insurance Company: ____________________
        Member ID: ___________________________
        Group Number: ________________________
        Policy Holder Name: __________________
        
        Signature: ___________________________
        Date: _______________________________
        """,
        
        'medical_history.pdf': """
        MEDICAL HISTORY FORM
        
        Patient Name: ________________________
        Date of Birth: _______________________
        
        Current Medications:
        1. ___________________________________
        2. ___________________________________
        3. ___________________________________
        
        Allergies:
        1. ___________________________________
        2. ___________________________________
        3. ___________________________________
        
        Past Medical History (check all that apply):
        [ ] Diabetes
        [ ] Hypertension
        [ ] Heart Disease
        [ ] Asthma
        [ ] Cancer
        [ ] Stroke
        [ ] Other: _____________________________
        
        Past Surgical History:
        1. ___________________________________
        2. ___________________________________
        
        Family Medical History:
        [ ] Diabetes
        [ ] Hypertension
        [ ] Heart Disease
        [ ] Cancer
        [ ] Other: _____________________________
        
        Social History:
        Tobacco Use: [ ] Yes [ ] No
        Alcohol Use: [ ] Yes [ ] No
        
        Signature: ___________________________
        Date: _______________________________
        """,
        
        'insurance_verification.pdf': """
        INSURANCE VERIFICATION FORM
        
        Patient Information:
        Full Name: ____________________________
        Date of Birth: ________________________
        
        Primary Insurance:
        Insurance Company: ____________________
        Member ID: ___________________________
        Group Number: ________________________
        Policy Holder Name: __________________
        Policy Holder DOB: ___________________
        Relationship to Patient: ______________
        
        Secondary Insurance (if applicable):
        Insurance Company: ____________________
        Member ID: ___________________________
        Group Number: ________________________
        Policy Holder Name: __________________
        Policy Holder DOB: ___________________
        Relationship to Patient: ______________
        
        Insurance Authorization:
        I authorize the release of any medical information necessary to process this claim.
        I authorize payment of medical benefits to the physician or supplier for services described.
        
        Signature: ___________________________
        Date: _______________________________
        """
    }
    
    # Create each form file
    for filename, content in sample_forms.items():
        file_path = forms_dir / filename
        
        # Only create if it doesn't exist
        if not file_path.exists():
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info(f"Created sample form: {filename}")
        else:
            logger.info(f"Sample form already exists: {filename}")
    
    return forms_dir

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_sample_forms()