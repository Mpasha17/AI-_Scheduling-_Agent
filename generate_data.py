import os
import logging
from pathlib import Path
from src.utils.database import initialize_database
from src.utils.generate_data import generate_synthetic_data
from src.utils.forms import create_sample_forms

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Create data directory if it doesn't exist
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'
    forms_dir = data_dir / 'forms'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(forms_dir, exist_ok=True)
    
    logger.info("Starting data generation process...")
    
    # Initialize database and generate synthetic data
    generate_synthetic_data(num_patients=50, num_days=30)
    
    logger.info("Data generation complete!")
    logger.info(f"Patient data saved to {data_dir / 'patients.csv'}")
    logger.info(f"Sample forms created in {forms_dir}")
    logger.info("You can now run the application with 'streamlit run app.py'")

if __name__ == "__main__":
    main()