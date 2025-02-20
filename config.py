from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TaskPriority:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

@dataclass
class TaskStatus:
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"

NOTION_CONFIG = {
    "database_properties": {
        "Title": {"title": {}},
        "Description": {"rich_text": {}},
        "Assignee": {"people": {}},
        "Due Date": {"date": {}},
        "Priority": {
            "select": {
                "options": [
                    {"name": TaskPriority.LOW, "color": "gray"},
                    {"name": TaskPriority.MEDIUM, "color": "blue"},
                    {"name": TaskPriority.HIGH, "color": "yellow"},
                    {"name": TaskPriority.URGENT, "color": "red"}
                ]
            }
        },
        "Status": {
            "select": {
                "options": [
                    {"name": TaskStatus.NOT_STARTED, "color": "default"},
                    {"name": TaskStatus.IN_PROGRESS, "color": "blue"},
                    {"name": TaskStatus.COMPLETED, "color": "green"},
                    {"name": TaskStatus.BLOCKED, "color": "red"}
                ]
            }
        }
    }
}