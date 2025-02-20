import os
from notion_client import Client
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("NOTION_KEY")

notion = Client(auth=key)
list_users_response = notion.users.list()
pprint(list_users_response)