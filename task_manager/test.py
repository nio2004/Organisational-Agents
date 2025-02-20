from datetime import datetime, timedelta
from task_manager.task_manager_functions import (
    create_task,
    update_task_status,
    get_tasks_by_status,
    generate_daily_report,
    send_reminders
)

def test_task_manager():
    print("\n--- Testing Task Manager Functions ---\n")
    
    # Step 1: Create a Task
    print("Creating a task...")
    task_response = create_task(
        title="Test Task Execution",
        description="Testing all task functionalities step by step.",
        assignee="hriteshkumarmaikap@gmail.com",  # Replace with a valid Notion user email
        due_date=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        priority="High"
    )
    print("Task Creation Response:", task_response)
    
    if task_response["status"] == "error":
        print("Task creation failed. Exiting tests.")
        return
    
    task_id = task_response["task_id"]
    
    # Step 2: Update Task Status
    print("\nUpdating task status to In Progress...")
    update_response = update_task_status(task_id, "In Progress")
    print("Update Response:", update_response)
    
    # Step 3: Get Tasks by Status
    print("\nFetching tasks with status 'In Progress'...")
    tasks_response = get_tasks_by_status("In Progress")
    print("Tasks Found:", tasks_response)
    
    # Step 4: Generate Daily Report
    print("\nGenerating daily report...")
    report_response = generate_daily_report()
    print("Daily Report:", report_response)
    
    # Step 5: Send Reminders
    print("\nSending reminders for tasks due tomorrow...")
    reminder_response = send_reminders()
    print("Reminder Response:", reminder_response)

if __name__ == "__main__":
    test_task_manager()
