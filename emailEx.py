import json
import os
from pydantic import BaseModel, Field
from groq import Groq
import instructor
from smolagents import Tool, HfApiModel, ToolCallingAgent

# Set up the Groq API key
os.environ["GROQ_API_KEY"] = os.environ["GROQ_API_KEY"]

# Define the Pydantic model for the response
class MeetingInfoResponseModel(BaseModel):
    date: str = Field(description="Extracted date of the meeting in YYYY-MM-DD format")
    title: str = Field(description="Extracted title of the meeting from the email")
    time: str = Field(description="Extracted time of the meeting in HH:MM format")
    sentiment_score: int = Field(description="Importance score of the meeting on a scale of 0-10")

# Patch Groq() with the instructor client
client = instructor.from_groq(Groq(), mode=instructor.Mode.JSON)

def extract_meeting_info(email_content: str) -> dict:
    """
    Extracts meeting date, time, and sentiment score from email content.
    Args:
        email_content (str): The email or message body.
    Returns:
        dict: Dictionary containing date, time, and sentiment score.
    """
    query = (
        "Extract the meeting date, time,title, and its importance sentiment score (0-10) from the given email. "
        "Return only a JSON object with 'date', 'time','title, and 'sentiment_score'. "
        "Ensure the date format is YYYY-MM-DD and time format is HH:MM."
        f"\n\nEmail Content: {email_content}"
    )

    system_prompt = (
        "You are an email analysis assistant. Your job is to extract structured meeting details from emails. "
        "Return the extracted date in 'YYYY-MM-DD', time in 'HH:MM', and sentiment score as an integer (0-10). "
        "If no time is mentioned, assume '09:00'. If no sentiment score is given, estimate based on urgency keywords and title."
    )

    try:
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
        
        return response.dict()
    except Exception as e:
        print(f"Error extracting meeting info: {str(e)}")
        return {"date": "","title":"" ,"time": "", "sentiment_score": 0}


# Define the Smol Agent Tool
class MeetingInfoExtractorTool(Tool):
    name = "meeting_info_extractor"
    description = "Extracts meeting details (date, time, title, and importance) from emails."
    inputs = {
        "email_content": {
            "type": "string",
            "description": "The email text from which to extract the meeting details.",
        }
    }
    output_type = "string"

    def forward(self, email_content: str) -> str:
        global allParam  # Use global variable
        meeting_info = extract_meeting_info(email_content)
        print("=======")
        print(meeting_info)
        allParam = meeting_info  # Now updates the global variable
        return json.dumps(meeting_info, indent=2)



# Initialize the agent with the custom tool
meeting_tool = MeetingInfoExtractorTool()
model = HfApiModel("Qwen/Qwen2.5-72B-Instruct")

agent = ToolCallingAgent(tools=[meeting_tool], model=model)

# Test the agent
email_text = """
Hey Team,

We need to discuss the upcoming product launch. Let's have a meeting on February 22, 2025, at 3 PM.
This is extremely urgent and critical for the project.

Best,
John
"""

agent_output = agent.run(f"Extract meeting details from this email: {email_text}")

print("Final output:")
print(agent_output)

print("=======")
print(allParam)
