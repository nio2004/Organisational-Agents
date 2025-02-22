import os
from typing import Dict, Any, List
from datetime import datetime
from smolagents import CodeAgent, HfApiModel
from dotenv import load_dotenv

# Import task and email-related tools
from task_manager.task_manager_functions import (
    create_task,
    update_task_status,
    get_tasks_by_status,
    send_reminders,
    get_tasks_by_priority,
    get_tasks_by_date,
    generate_daily_report,
    update_task_priority,
    update_task_due_date,
    get_task_details,
    get_overdue_tasks
)

from email_manager.emailTools import extract_meeting_info

class UnifiedTaskAgent:
    def __init__(self, token: str, model_name: str = "Qwen/Qwen2.5-Coder-32B-Instruct"):
        """
        Unified agent for task and email processing.

        Args:
            token: HuggingFace API token
            model_name: Model used for inference
        """
        self.model = HfApiModel(
            model_id=model_name,
            token=token
        )

        self.tools = [
            create_task,
            update_task_status,
            get_tasks_by_status,
            send_reminders,
            get_tasks_by_priority,
            get_tasks_by_date,
            generate_daily_report,
            update_task_priority,
            update_task_due_date,
            get_task_details,
            get_overdue_tasks,
            extract_meeting_info,
        ]

        self.agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            add_base_tools=True
        )

        self.current_user = "hriteshkumarmaikap@gmail.com"
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def process_task_query(self, user_query: str) -> str:
        """
        Handles natural language task queries.
        """
        contextualized_query = f"""
        Current User: {self.current_user}
        Current Time: {self.current_time}
        
        User Query: {user_query}
        """
        return self.agent.run(contextualized_query)

    def process_email(self, email_content: str) -> Dict[str, Any]:
        """
        Extracts meeting information from emails and creates tasks automatically using SmolAgents.
        """
        category = "Meeting Schedule"
        extracted_info = extract_meeting_info(email_content)

        if extracted_info  and extracted_info.get("status") == "success":
            meeting_info = extracted_info.get("meeting_info", {})
            task_description = f"Meeting: {meeting_info.get('title', 'No Title')}"
            due_date = meeting_info.get('date', self.current_time)
            assignee = self.current_user
            priority = meeting_info.get('sentiment_score', 'Normal')
            
            # Use the agent to create a task
            task_query = f"Create a task called '{task_description}' assigned to '{assignee}' due '{due_date}' with priority '{priority}'."
            response = self.agent.run(task_query)
            
            extracted_info["task_created"] = response

        return {"category": category, "extracted_info": extracted_info}


def display_help():
    """Display available commands."""
    print("\nAvailable Commands:")
    print("-" * 50)
    print("1. Create Task: 'create a task called [title] due [date]'")
    print("2. Update Status: 'update status of task [id] to [status]'")
    print("3. Check Tasks: 'show all [status] tasks'")
    print("4. Task Details: 'show details for task [id]'")
    print("5. Daily Report: 'generate daily report'")
    print("6. Overdue Tasks: 'show overdue tasks'")
    print("7. Send Reminders: 'send task reminders'")
    print("8. Process Email: 'process email [email content]'")
    print("9. Help: 'help'")
    print("10. Exit: 'exit'")
    print("-" * 50)


def main():
    load_dotenv()
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("Error: HF_TOKEN not found in environment variables")
        return

    agent = UnifiedTaskAgent(token=hf_token)

    print("\n=== Unified Task & Email Processing Assistant ===")
    print("Current User:", agent.current_user)
    print("Current Time:", agent.current_time)
    display_help()

    while True:
        try:
            user_input = input("\nHow can I assist? ").strip()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                display_help()
                continue

            if user_input.lower().startswith("process email"):
                email_content = user_input.replace("process email", "").strip()
                response = agent.process_email(email_content)
            else:
                response = agent.process_task_query(user_input)

            print("\nResponse:")
            print("-" * 50)
            print(response)
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or type 'help' for available commands.")

if __name__ == "__main__":
    main()

