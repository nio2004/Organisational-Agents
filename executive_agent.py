from typing import Dict, Any, List
from datetime import datetime, timedelta
from smolagents import CodeAgent, HfApiModel
import os
from dotenv import load_dotenv

# Import all tools from task_manager_functions
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

class TaskManagerAgent:
    def __init__(self, token: str, model_name: str = "Qwen/Qwen2.5-Coder-32B-Instruct"):
        """
        Initialize the Task Manager Agent with tools and model
        
        Args:
            token: HuggingFace API token
            model_name: The name of the model to use for the agent
        """
        # Initialize the model with token
        self.model = HfApiModel(
            model_id=model_name,
            token=token
        )
        
        # Define all available tools as a list
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
            get_overdue_tasks
        ]
        
        # Create the CodeAgent with tools
        self.agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            add_base_tools=True
        )
        
        # Store current user and time information
        self.current_user = "hriteshkumarmaikap@gmail.com"
        self.current_time = "2025-02-21 05:12:32"
    
    def run(self, user_query: str) -> str:
        """
        Process a user query and execute the appropriate task management action
        
        Args:
            user_query: The natural language query from the user
            
        Returns:
            Response with the results of processing the query
        """
        # Add context to the user query
        contextualized_query = f"""
        Current User: {self.current_user}
        Current Time: {self.current_time}
        
        User Query: {user_query}
        
        Please help with this task management request. Available actions include:
        - Creating new tasks
        - Updating task status/priority/due dates
        - Checking task status and details
        - Generating reports
        - Sending reminders
        - Finding overdue tasks
        """
        
        # Process the user query through the agent
        result = self.agent.run(contextualized_query)
        return result

def display_help():
    """Display available commands and their descriptions"""
    print("\nAvailable Commands:")
    print("-" * 50)
    print("1. Create Task: 'create a task called [title] due [date]'")
    print("2. Update Status: 'update status of task [id] to [status]'")
    print("3. Check Tasks: 'show all [status] tasks'")
    print("4. Task Details: 'show details for task [id]'")
    print("5. Daily Report: 'generate daily report'")
    print("6. Overdue Tasks: 'show overdue tasks'")
    print("7. Send Reminders: 'send task reminders'")
    print("8. Help: 'help'")
    print("9. Exit: 'exit'")
    print("-" * 50)

def main():
    # Load environment variables
    load_dotenv()
    
    # Get HuggingFace API token
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("Error: HF_TOKEN not found in environment variables")
        return
    
    try:
        # Create task manager agent
        task_agent = TaskManagerAgent(token=hf_token)
        
        print("\n=== Task Management Assistant ===")
        print("Current User:", task_agent.current_user)
        print("Current Time:", task_agent.current_time)
        display_help()
        
        while True:
            try:
                user_input = input("\nHow can I help with your tasks? ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye!")
                    break
                    
                if user_input.lower() == 'help':
                    display_help()
                    continue
                
                # Process the request
                response = task_agent.run(user_input)
                
                # Pretty print the response
                print("\nResponse:")
                print("-" * 50)
                print(response)
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError processing request: {str(e)}")
                print("Please try again or type 'help' for available commands.")
    
    except Exception as e:
        print(f"Error initializing agent: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()