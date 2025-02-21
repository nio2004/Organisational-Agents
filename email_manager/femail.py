from typing import Dict, Any
import os
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from groq import Groq
import instructor

# Initialize Groq client
os.environ["GROQ_API_KEY"] = os.environ["GROQ_API_KEY"]
client = instructor.from_groq(Groq(), mode=instructor.Mode.JSON)

class MeetingInfoResponseModel(BaseModel):
    date: str = Field(description="Extracted date of the meeting in YYYY-MM-DD format")
    title: str = Field(description="Extracted title of the meeting from the email")
    time: str = Field(description="Extracted time of the meeting in HH:MM format")
    sentiment_score: int = Field(description="Importance score of the meeting on a scale of 0-10")
    description: str = Field(description="Description of the meeting")

class TaskInfoResponseModel(BaseModel):
    date: str = Field(description="Extracted date of the task in YYYY-MM-DD format")
    title: str = Field(description="Extracted title of the task from the email")

class EmailClassificationResponseModel(BaseModel):
    category: str = Field(description="Classified category of the email: 'Task Creation', 'Meeting Schedule', or 'Both'")

def classify_email(email_content: str) -> Dict[str, Any]:
    try:
        query = (
            "Analyze the given email content and classify it into one of the following categories: "
            "'Task Creation' if it contains a request to perform or complete a task, "
            "'Meeting Schedule' if it contains details about a meeting, "
            "or 'Both' if it includes both elements. "
            "Return only a JSON object with the key 'category'. "
            f"\n\nEmail Content: {email_content}"
        )

        system_prompt = (
            "You are an email classification assistant. Your job is to analyze emails and classify them into three categories: "
            "'Task Creation' if the email contains a request or instruction to perform a task, "
            "'Meeting Schedule' if it discusses scheduling a meeting, "
            "or 'Both' if it contains elements of both. "
            "Return only the classification result in a JSON object."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=EmailClassificationResponseModel,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        return response.dict()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def extract_task_info(email_content: str) -> Dict[str, Any]:
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
        
        return response.dict()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def extract_meeting_info(email_content: str) -> Dict[str, Any]:
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
        
        return response.dict()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_email(email_content: str) -> Dict[str, Any]:
    classification = classify_email(email_content)
    category = classification.get("category", "Unknown")
    
    extracted_info = {"category": category}
    
    if category == "Meeting Schedule":
        extracted_info["meeting_info"] = extract_meeting_info(email_content)
    elif category == "Task Creation":
        extracted_info["task_info"] = extract_task_info(email_content)
    elif category == "Both":
        extracted_info["meeting_info"] = extract_meeting_info(email_content)
        extracted_info["task_info"] = extract_task_info(email_content)
    
    return extracted_info

# Example Email Inputs
test_email_1 = """
    Hi Team,
    
    We have an important client meeting scheduled for March 5, 2025, at 10:30 AM.
    Please ensure to review the project updates before joining.
    
    Thanks,
    Manager
"""

test_email_2 = """
    Hello,
    
    Please complete the sales report submission by March 4, 2025.
    It is crucial for our quarterly review.
    
    Regards,
    Supervisor
"""

test_email_3 = """
    Hey Team,
    
    We need to schedule a meeting on March 6, 2025, at 3:00 PM to discuss the product launch.
    Also, please complete the feature documentation by March 5, 2025.
    
    Best,
    Project Lead
"""

print(process_email(test_email_1))  # Should extract meeting info
print(process_email(test_email_2))  # Should extract task info
print(process_email(test_email_3))  # Should extract both meeting and task info
