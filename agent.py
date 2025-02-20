from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel
from smolagents.agents import ToolCallingAgent
from smolagents import tool, TransformersModel, LiteLLMModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('token')
# Corrected model initialization with environment variable
model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct", token = key)

agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)
agent.run("Search and let me know how to generate notion api key")