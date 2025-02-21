from typing import Dict, Any
import os
from datetime import datetime
from pydantic import BaseModel, Field
from groq import Groq
import instructor
from smolagents import tool

# Initialize Groq client
os.environ["GROQ_API_KEY"] = os.environ["GROQ_API_KEY"]
client = instructor.from_groq(Groq(), mode=instructor.Mode.JSON)

class MeetingInfoResponseModel(BaseModel):
    date: str = Field(description="Extracted date of the meeting in YYYY-MM-DD format")
    title: str = Field(description="Extracted title of the meeting from the email")
    time: str = Field(description="Extracted time of the meeting in HH:MM format")
    sentiment_score: int = Field(description="Importance score of the meeting on a scale of 0-10")
    description: str = Field(description="Description of the meeting")

@tool
def extract_meeting_info(email_content: str) -> Dict[str, Any]:
    """
    Extracts meeting information from email content using Groq API.
    
    Args:
        email_content: The email text to analyze
    
    Returns:
        Dict containing meeting details and extraction status
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=MeetingInfoResponseModel,
            messages=[
                {"role": "system", "content": "Extract meeting details including date, time, title, description, and priority score."},
                {"role": "user", "content": email_content}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        return {
            "status": "success",
            "meeting_info": response.dict(),
            "extracted_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

class TaskInfoResponseModel(BaseModel):
    date: str = Field(description="Extracted date of the task in YYYY-MM-DD format")
    title: str = Field(description="Extracted title of the task from the email")

@tool
def extract_task_info(email_content: str) -> Dict[str, Any]:
    """
    Extracts task information from email content using Groq API.
    
    Args:
        email_content: The email text to analyze
    
    Returns:
        Dict containing task details and extraction status
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=TaskInfoResponseModel,
            messages=[
                {"role": "system", "content": "Extract task details including title and date."},
                {"role": "user", "content": email_content}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        return {
            "status": "success",
            "task_info": response.dict(),
            "extracted_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

class EmailClassificationResponseModel(BaseModel):
    category: str = Field(description="Classified category of the email: 'Task Creation', 'Meeting Schedule', or 'Both'")

@tool
def classify_email(email_content: str) -> Dict[str, Any]:
    """
    Classifies the email content into categories: 'Task Creation', 'Meeting Schedule', or 'Both'.
    
    Args:
        email_content: The email text to analyze
    
    Returns:
        Dict containing classification result and status
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=EmailClassificationResponseModel,
            messages=[
                {"role": "system", "content": "Classify the email as 'Task Creation', 'Meeting Schedule', or 'Both'."},
                {"role": "user", "content": email_content}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        return {
            "status": "success",
            "classification": response.dict(),
            "classified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

@tool
def process_email(email_content: str) -> Dict[str, Any]:
    """
    Processes an email to classify it and extract relevant task or meeting details.
    
    Args:
        email_content: The email text to analyze
    
    Returns:
        Dict containing classification and extracted information
    """
    classification = classify_email(email_content)
    category = classification.get("classification", {}).get("category", "Unknown")
    
    extracted_info = {"category": category}
    
    if category == "Meeting Schedule":
        extracted_info["meeting_info"] = extract_meeting_info(email_content)
    elif category == "Task Creation":
        extracted_info["task_info"] = extract_task_info(email_content)
    elif category == "Both":
        extracted_info["meeting_info"] = extract_meeting_info(email_content)
        extracted_info["task_info"] = extract_task_info(email_content)
    
    return extracted_info