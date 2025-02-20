# Task Management Agent

A sophisticated task management system that integrates with Notion for effective task tracking and management.

## Features

- Task creation and management
- Priority-based task organization
- Deadline tracking and reminders
- Resource allocation
- Daily progress reporting
- Notion integration

## Setup

1. Install dependencies:
```bash
pip install smolagents notion-client python-dotenv
```

2. Create a `.env` file with your credentials:
```
NOTION_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id
HF_TOKEN=your_huggingface_token
```

3. Create a Notion database with the required properties (see config.py for structure)

## Usage

```python
from task_manager_agent import TaskManagerAgent

# Initialize the agent
agent = TaskManagerAgent()

# Create a new task
agent.create_task(
    title="Example Task",
    description="Task description",
    assignee="user@example.com",
    due_date="2025-03-01",
    priority="High"
)

# Generate daily report
report = agent.generate_daily_report()
```

## Configuration

The agent uses a configuration defined in `config.py` that specifies:
- Task priority levels
- Task statuses
- Notion database properties

## Tools

The agent includes several tools:
- task_creator: Creates new tasks in Notion
- deadline_calculator: Manages and tracks task deadlines
- resource_allocator: Assigns tasks to team members
- dependency_analyzer: Tracks task dependencies
- workload_balancer: Ensures balanced task distribution

## Error Handling

The agent includes comprehensive error handling for:
- Notion API interactions
- Invalid task parameters
- User authentication issues
- Database queries