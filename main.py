# main.py
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from config import TaskPriority, TaskStatus
from task_manager_functions import (
    create_task,
    generate_daily_report,
    send_reminders
)

load_dotenv()

def main() -> None:
    try:
        # Create a new task
        task = create_task(
            title="Implement User Authentication",
            description="Add OAuth2 authentication to the API endpoints",
            assignee="hriteshkumarmaikap@gmail.com",
            due_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            priority=TaskPriority.HIGH
        )
        
        # Print the result
        print("\nTask Creation Result:")
        print(task)
        
        # Generate daily report
        report = generate_daily_report()
        print("\nDaily Task Report:")
        if report.get("status") != "error":
            for status, count in report["summary"].items():
                print(f"{status}: {count} tasks")
            
            print("\nPriority Distribution:")
            for priority, count in report["priority_distribution"].items():
                print(f"{priority}: {count} tasks")
        else:
            print(f"Error generating report: {report['message']}")
        
        # Send reminders for tasks due tomorrow
        due_tasks = send_reminders()
        print(f"\nReminders for tomorrow:")
        if due_tasks.get("status") != "error":
            print(f"Found {due_tasks['count']} tasks due tomorrow")
            for reminder in due_tasks["reminders"]:
                print(f"- {reminder['title']} (Assigned to: {reminder['assignee']})")
        else:
            print(f"Error sending reminders: {due_tasks['message']}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()