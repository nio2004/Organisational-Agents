from dataclasses import dataclass
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TaskPriority:
    URGENT = "Urgent"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

@dataclass
class TaskStatus:
    BLOCKED = "Blocked"
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

@dataclass
class SystemMetadata:
    CURRENT_USER = "hriteshMaikap"
    LAST_UPDATED = "2025-02-20 11:14:52"
    TIME_ZONE = "UTC"

NOTION_CONFIG = {
    "database_id": os.getenv("NOTION_DATABASE_ID"),
    "database_properties": {
        "Priority": {
            "select": {
                "options": [
                    {"name": TaskPriority.URGENT, "color": "red"},
                    {"name": TaskPriority.HIGH, "color": "yellow"},
                    {"name": TaskPriority.MEDIUM, "color": "blue"},
                    {"name": TaskPriority.LOW, "color": "gray"}
                ]
            }
        },
        "Description": {"rich_text": {}},
        "Due Date": {"date": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": TaskStatus.BLOCKED, "color": "red"},
                    {"name": TaskStatus.NOT_STARTED, "color": "default"},
                    {"name": TaskStatus.IN_PROGRESS, "color": "blue"},
                    {"name": TaskStatus.COMPLETED, "color": "green"}
                ]
            }
        },
        "Assignee": {"people": {}},
        "Title": {"title": {}}
    }
}

def get_current_user():
    """Returns the current user's login"""
    return SystemMetadata.CURRENT_USER

def get_last_updated():
    """Returns the last updated timestamp"""
    return datetime.strptime(SystemMetadata.LAST_UPDATED, "%Y-%m-%d %H:%M:%S")

def is_database_configured():
    """Checks if the database ID is properly configured"""
    return bool(NOTION_CONFIG["database_id"])