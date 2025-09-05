from typing import Dict, List, Optional, Any
import os
import json
import logging
from datetime import datetime

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain.schema import SystemMessage, HumanMessage
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage

from src.config import MISTRAL_API_KEY
from src.agents.tools import get_scheduling_tools

logger = logging.getLogger(__name__)

class SchedulingAgent:
    """Medical appointment scheduling agent using LangChain and MistralAI"""
    
    def __init__(self):
        """Initialize the scheduling agent with LLM and tools"""
        self.llm = self._init_llm()
        self.tools = get_scheduling_tools()
        self.agent_executor = self._setup_agent()
        self.messages = []
        self.patient_info = {}
    
    def _init_llm(self) -> ChatMistralAI:
        """Initialize the Mistral LLM"""
        return ChatMistralAI(
            model="mistral-large-latest",
            mistral_api_key=MISTRAL_API_KEY,
            temperature=0.2,
            max_tokens=1024
        )
    
    def _setup_agent(self) -> AgentExecutor:
        """Set up the LangChain agent with tools and prompt"""
        # System prompt for the scheduling agent
        system_prompt = """
        You are a medical appointment scheduling assistant for a healthcare clinic. 
        Your job is to help patients schedule appointments with doctors, collect necessary information, 
        and ensure all paperwork is properly handled.
        
        Follow these guidelines:
        1. Be professional, friendly, and empathetic in all interactions
        2. Collect patient information accurately (name, DOB, contact details)
        3. For new patients, schedule 60-minute appointments; for returning patients, schedule 30-minute appointments
        4. Always verify insurance information
        5. Send confirmation and intake forms after booking
        6. Set up reminders for the appointment
        7. Export appointment details for admin review when complete
        
        IMPORTANT: Always maintain patient privacy and handle all information securely.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = {
            "input": lambda x: x["input"],
            "chat_history": lambda x: x["chat_history"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        } | prompt | self.llm | OpenAIFunctionsAgentOutputParser()
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="generate"
        )
    
    def process_message(self, user_input: str) -> str:
        """Process a user message and return the agent's response"""
        try:
            # Extract patient info from the message if possible
            self._extract_patient_info(user_input)
            
            # Run the agent
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": self.messages
            })
            
            # Update chat history
            self.messages.append(HumanMessage(content=user_input))
            self.messages.append(AIMessage(content=result["output"]))
            
            return result["output"]
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."
    
    def _extract_patient_info(self, message: str) -> None:
        """Extract patient information from the message using simple heuristics"""
        # This is a simple implementation - in a real system, you would use more sophisticated NLP
        # Look for name patterns
        if "name is" in message.lower():
            name_parts = message.split("name is")[1].strip().split()
            if len(name_parts) >= 2:
                self.patient_info["first_name"] = name_parts[0].strip(",.")
                self.patient_info["last_name"] = name_parts[1].strip(",.") 
        
        # Look for DOB patterns
        if "born on" in message.lower() or "dob" in message.lower() or "date of birth" in message.lower():
            # Simple pattern matching for dates
            # In a real system, use a more robust date parser
            for word in message.split():
                if "/" in word and len(word) >= 8:
                    self.patient_info["date_of_birth"] = word
                    break
    
    def reset_conversation(self) -> None:
        """Reset the conversation history and patient info"""
        self.messages = []
        self.patient_info = {}