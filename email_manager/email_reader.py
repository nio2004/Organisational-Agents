from typing import Dict, Any
import os
from datetime import datetime, timedelta
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
        query = (
            "Extract the meeting date, time, title, description, and its importance sentiment score (0-10) from the given email. "
            "Return only a JSON object with 'date', 'time', 'title', 'description', and 'sentiment_score'. "
            "Ensure the date format is YYYY-MM-DD and time format is HH:MM."
            f"\n\nEmail Content: {email_content}"
        )

        system_prompt = (
            "You are an email analysis assistant. Your job is to extract structured meeting details from emails. "
            "Return the extracted date in 'YYYY-MM-DD', time in 'HH:MM', and sentiment score as an integer (0-10). "
            "If no explicit date is found, use the date one day after the current date. If no time is mentioned, assume '09:00'. If no sentiment score is given, estimate based on urgency keywords and title."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=MeetingInfoResponseModel,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
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