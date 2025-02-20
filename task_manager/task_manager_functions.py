# task_manager_functions.py
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from smolagents import tool
from notion_client import Client
import os
from dotenv import load_dotenv
from task_manager.config import NOTION_CONFIG, TaskPriority, TaskStatus, SystemMetadata

load_dotenv()
NOTION_KEY = os.getenv("NOTION_KEY")
database_id = NOTION_CONFIG["database_id"]
current_user = SystemMetadata.CURRENT_USER

# Initialize Notion client
notion = Client(auth=NOTION_KEY)

@tool
def create_task(
    title: str,
    description: str,
    assignee: str,
    due_date: str,
    priority: str = TaskPriority.MEDIUM
) -> Dict[str, Any]:
    """Creates a new task in Notion database
    
    Args:
        title: The title of the task
        description: Detailed description of the task
        assignee: Email address of the person assigned to the task
        due_date: Due date in YYYY-MM-DD format
        priority: Task priority level (HIGH, MEDIUM, LOW)
        
    Returns:
        Dict with task creation status and details
    """
    try:
        if priority not in [getattr(TaskPriority, p) for p in dir(TaskPriority) if not p.startswith("_")]:
            priority = TaskPriority.MEDIUM

        task = {
            "parent": {"database_id": database_id},
            "properties": {
                "Title": {"title": [{"text": {"content": title}}]},
                "Description": {"rich_text": [{"text": {"content": description}}]},
                "Assignee": {"people": [{"id": _get_user_id(assignee)}]},
                "Due Date": {"date": {"start": due_date}},
                "Priority": {"select": {"name": priority}},
                "Status": {"select": {"name": TaskStatus.NOT_STARTED}}
            }
        }
        result = notion.pages.create(**task)
        return {
            "status": "success",
            "task_id": result["id"],
            "created_by": current_user,
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

@tool
def update_task_status(
    task_id: str,
    status: str
) -> Dict[str, Any]:
    """Updates the status of an existing task
    
    Args:
        task_id: The unique identifier of the task to update
        status: New status value for the task
        
    Returns:
        Dict with update status and details
    """
    try:
        if status not in [getattr(TaskStatus, s) for s in dir(TaskStatus) if not s.startswith("_")]:
            raise ValueError(f"Invalid status: {status}")

        result = notion.pages.update(
            page_id=task_id,
            properties={"Status": {"select": {"name": status}}}
        )
        return {
            "status": "success",
            "task_id": task_id,
            "new_status": status,
            "updated_by": current_user,
            "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

@tool
def get_tasks_by_status(
    status: str
) -> Dict[str, Any]:
    """Retrieves tasks filtered by status
    
    Args:
        status: Status value to filter tasks by
        
    Returns:
        Dict containing matching tasks and count
    """
    try:
        if status not in [getattr(TaskStatus, s) for s in dir(TaskStatus) if not s.startswith("_")]:
            raise ValueError(f"Invalid status: {status}")

        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Status",
                "select": {"equals": status}
            },
            sorts=[{
                "property": "Due Date",
                "direction": "ascending"
            }]
        )
        
        tasks = []
        for page in response["results"]:
            task = {
                "id": page["id"],
                "title": page["properties"]["Title"]["title"][0]["text"]["content"],
                "status": status,
                "due_date": page["properties"]["Due Date"]["date"]["start"],
                "priority": page["properties"]["Priority"]["select"]["name"]
            }
            tasks.append(task)
        
        return {
            "status": "success",
            "tasks": tasks,
            "count": len(tasks),
            "queried_by": current_user,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

@tool
def send_reminders() -> Dict[str, Any]:
    """Sends reminders for tasks due tomorrow
    
    Returns:
        Dict containing list of tasks due tomorrow and count
    """
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "and": [
                    {
                        "property": "Due Date",
                        "date": {"equals": tomorrow}
                    },
                    {
                        "property": "Status",
                        "select": {
                            "does_not_equal": TaskStatus.COMPLETED
                        }
                    }
                ]
            }
        )
        
        reminders = []
        for page in response["results"]:
            reminder = {
                "task_id": page["id"],
                "title": page["properties"]["Title"]["title"][0]["text"]["content"],
                "assignee": page["properties"]["Assignee"]["people"][0]["name"],
                "due_date": tomorrow,
                "status": page["properties"]["Status"]["select"]["name"]
            }
            reminders.append(reminder)
        
        return {
            "status": "success",
            "reminders": reminders,
            "count": len(reminders),
            "generated_by": current_user,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

def _get_user_id(email: str) -> Optional[str]:
    """Helper method to get Notion user ID from email
    
    Args:
        email: Email address of the Notion user
        
    Returns:
        User ID string or None if not found
    """
    try:
        users = notion.users.list()
        for user in users["results"]:
            if user.get("person", {}).get("email") == email:
                return user["id"]
        return None  # Return None if no matching email is found
    except Exception as e:
        print(f"Error getting user ID: {str(e)}")
        return None

def generate_daily_report() -> Dict[str, Any]:
    """Generates a daily progress report of all tasks
    
    Returns:
        Dict containing task summary and breakdown by status/priority
    """
    try:
        report = {
            "summary": {},
            "details": [],
            "generated_by": current_user,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Get counts for each status
        for status in [getattr(TaskStatus, s) for s in dir(TaskStatus) if not s.startswith("_")]:
            tasks = get_tasks_by_status(status)
            if tasks.get("status") == "success":
                report["summary"][status] = tasks["count"]
                report["details"].extend(tasks["tasks"])
        
        # Add priority distribution
        priority_counts = {}
        for task in report["details"]:
            priority = task["priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        report["priority_distribution"] = priority_counts
        
        return report
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }