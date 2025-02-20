from task_manager_agent import TaskManagerAgent
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # Initialize the task manager agent
    agent = TaskManagerAgent()
    
    # Example usage
    # Create a new task
    task = agent.create_task(
        title="Implement User Authentication",
        description="Add OAuth2 authentication to the API endpoints",
        assignee="developer@example.com",
        due_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        priority="High"
    )
    
    # Generate daily report
    report = agent.generate_daily_report()
    print("Daily Task Report:")
    for status, count in report.items():
        print(f"{status}: {count} tasks")
    
    # Send reminders for tasks due tomorrow
    due_tasks = agent.send_reminders()
    print(f"\nFound {len(due_tasks)} tasks due tomorrow")

if __name__ == "__main__":
    main()