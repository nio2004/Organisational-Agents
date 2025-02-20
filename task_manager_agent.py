from typing import Optional, List, Dict
from datetime import datetime, timedelta
from smolagents import CodeAgent, tool
from smolagents.agents import ToolCallingAgent
from smolagents import HfApiModel
from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()
NOTION_KEY = os.getenv("NOTION_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

class TaskManagerAgent(ToolCallingAgent):
    def __init__(self):
        super().__init__()
        self.notion = Client(auth=NOTION_KEY)
        self.model = HfApiModel(
            model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
            token=HF_TOKEN
        )
        
    @tool
    def create_task(self, title: str, description: str, assignee: str, 
                    due_date: str, priority: str = "Medium") -> Dict:
        """Creates a new task in Notion database"""
        try:
            task = {
                "parent": {"database_id": os.getenv("NOTION_DATABASE_ID")},
                "properties": {
                    "Title": {"title": [{"text": {"content": title}}]},
                    "Description": {"rich_text": [{"text": {"content": description}}]},
                    "Assignee": {"people": [{"id": self._get_user_id(assignee)}]},
                    "Due Date": {"date": {"start": due_date}},
                    "Priority": {"select": {"name": priority}},
                    "Status": {"select": {"name": "Not Started"}}
                }
            }
            return self.notion.pages.create(**task)
        except Exception as e:
            return {"error": str(e)}

    @tool
    def update_task_status(self, task_id: str, status: str) -> Dict:
        """Updates the status of an existing task"""
        try:
            return self.notion.pages.update(
                page_id=task_id,
                properties={"Status": {"select": {"name": status}}}
            )
        except Exception as e:
            return {"error": str(e)}

    @tool
    def get_tasks_by_status(self, status: str) -> List[Dict]:
        """Retrieves tasks filtered by status"""
        try:
            response = self.notion.databases.query(
                database_id=os.getenv("NOTION_DATABASE_ID"),
                filter={
                    "property": "Status",
                    "select": {"equals": status}
                }
            )
            return response["results"]
        except Exception as e:
            return {"error": str(e)}

    @tool
    def send_reminders(self) -> List[Dict]:
        """Sends reminders for tasks due soon"""
        try:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            response = self.notion.databases.query(
                database_id=os.getenv("NOTION_DATABASE_ID"),
                filter={
                    "and": [
                        {
                            "property": "Due Date",
                            "date": {"equals": tomorrow}
                        },
                        {
                            "property": "Status",
                            "select": {
                                "does_not_equal": "Completed"
                            }
                        }
                    ]
                }
            )
            # Here you would implement actual notification logic
            return response["results"]
        except Exception as e:
            return {"error": str(e)}

    def _get_user_id(self, email: str) -> Optional[str]:
        """Helper method to get Notion user ID from email"""
        users = self.notion.users.list()
        for user in users["results"]:
            if user.get("person", {}).get("email") == email:
                return user["id"]
        return None

    def generate_daily_report(self) -> Dict:
        """Generates a daily progress report"""
        try:
            statuses = ["Not Started", "In Progress", "Completed"]
            report = {}
            for status in statuses:
                tasks = self.get_tasks_by_status(status)
                report[status] = len(tasks)
            return report
        except Exception as e:
            return {"error": str(e)}