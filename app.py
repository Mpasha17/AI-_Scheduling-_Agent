import os
import logging
import streamlit as st
from datetime import datetime

from src.agents.scheduling_agent import SchedulingAgent
from src.utils.database import initialize_database
from src.utils.generate_data import generate_synthetic_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database and synthetic data if needed
def initialize_data():
    """Initialize database and synthetic data if needed"""
    db_initialized = initialize_database()
    if db_initialized:
        # Check if we need to generate synthetic data
        # In a real app, you would check if data already exists
        generate_synthetic_data(num_patients=50, num_days=30)
    return db_initialized

# Initialize the scheduling agent
def get_agent():
    """Get or create the scheduling agent"""
    if 'agent' not in st.session_state:
        st.session_state.agent = SchedulingAgent()
    return st.session_state.agent

# Main app
def main():
    st.set_page_config(
        page_title="Medical Appointment Scheduler",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("Medical Appointment Scheduler")
    
    # Initialize data
    if 'initialized' not in st.session_state:
        with st.spinner("Initializing database and synthetic data..."):
            st.session_state.initialized = initialize_data()
    
    # Sidebar
    st.sidebar.title("About")
    st.sidebar.info(
        "This is a medical appointment scheduling assistant. "
        "It helps patients schedule appointments with doctors, "
        "collects necessary information, and ensures all paperwork is properly handled."
    )
    
    # Reset button
    if st.sidebar.button("Reset Conversation"):
        if 'agent' in st.session_state:
            st.session_state.agent.reset_conversation()
        if 'messages' in st.session_state:
            st.session_state.messages = []
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("How can I help you schedule your appointment today?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                agent = get_agent()
                response = agent.process_message(prompt)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()