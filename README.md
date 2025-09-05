# Medical Appointment Scheduling AI Agent

This project implements an AI-powered medical appointment scheduling agent that automates patient booking, reduces no-shows, and streamlines clinic operations.

## Features

- Patient greeting and data collection
- Patient lookup in EMR database
- Smart scheduling based on patient type
- Calendar integration for appointment booking
- Insurance information collection
- Appointment confirmation and export
- Form distribution to patients
- Automated reminder system

## Technical Stack

- LangChain and LangGraph for agent orchestration
- Mistral AI for natural language processing
- SQLite for database storage
- Streamlit for user interface

## Project Structure

```
├── app.py                  # Main Streamlit application
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── .env                    # Environment variables (add to .gitignore)
├── data/                   # Data directory
│   ├── patients.csv        # Synthetic patient data
│   ├── doctor_schedules.xlsx # Doctor availability
│   └── forms/              # Patient intake forms
├── database/               # Database files
│   └── medical_db.sqlite   # SQLite database
├── src/                    # Source code
│   ├── agents/             # Agent definitions
│   │   ├── __init__.py
│   │   ├── greeting_agent.py
│   │   ├── scheduling_agent.py
│   │   ├── insurance_agent.py
│   │   └── reminder_agent.py
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   └── insurance.py
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── calendar.py
│   │   ├── email.py
│   │   └── sms.py
│   └── config.py           # Configuration settings
└── tests/                  # Test files
    ├── __init__.py
    ├── test_agents.py
    ├── test_models.py
    └── test_utils.py
```

## Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys (see `.env.example`)
4. Run the application: `streamlit run app.py`

## Usage

The application provides a chat interface where patients can:

1. Enter their personal information
2. Schedule an appointment with a doctor
3. Provide insurance information
4. Receive confirmation and reminders

## Development

- Generate synthetic patient data: `python src/utils/generate_data.py`
- Run tests: `pytest tests/`

## License

MIT