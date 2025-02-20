# Updated NOTION_CONFIG based on actual database properties
NOTION_CONFIG = {
    "database_id": "1a0d7db3-8544-80bc-b66f-c36c42604466",
    "database_properties": {
        "Priority": {
            "select": {
                "options": [
                    {"name": "Urgent", "color": "red"},
                    {"name": "High", "color": "yellow"},
                    {"name": "Medium", "color": "blue"},
                    {"name": "Low", "color": "gray"}
                ]
            }
        },
        "Description": {"rich_text": {}},
        "Due Date": {"date": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Blocked", "color": "red"},
                    {"name": "Not Started", "color": "default"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Completed", "color": "green"}
                ]
            }
        },
        "Assignee": {"people": {}},
        "Title": {"title": {}},
    }
}