import requests
import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

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

def get_database_properties(notion_token: str, database_id: str) -> Dict[str, Any]:
    """
    Get property information for a specific database
    
    Args:
        notion_token (str): Your Notion API token
        database_id (str): ID of the database to check
        
    Returns:
        Dict[str, Any]: Database properties information
    """
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.notion.com/v1/databases/{database_id}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get database: {response.status_code}")
            print(f"   Error: {response.text}")
            return {}
            
        database_data = response.json()
        return database_data.get("properties", {})
        
    except Exception as e:
        print(f"❌ Error retrieving database: {str(e)}")
        return {}

def compare_properties(actual_properties: Dict[str, Any], expected_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare actual database properties with expected configuration
    
    Args:
        actual_properties: Properties fetched from Notion API
        expected_config: Configuration from config.py
        
    Returns:
        Dict with comparison results
    """
    expected_properties = expected_config["database_properties"]
    
    # Initialize results
    results = {
        "matching_properties": [],
        "type_mismatches": [],
        "missing_in_db": [],
        "extra_in_db": [],
        "select_option_differences": {}
    }
    
    # Check for expected properties
    actual_property_names = set(actual_properties.keys())
    expected_property_names = set(expected_properties.keys())
    
    # Find properties in expected config but missing in actual DB
    results["missing_in_db"] = list(expected_property_names - actual_property_names)
    
    # Find extra properties in actual DB not in expected config
    results["extra_in_db"] = list(actual_property_names - expected_property_names)
    
    # For properties present in both, check type matches
    for prop_name in expected_property_names.intersection(actual_property_names):
        expected_type = next(iter(expected_properties[prop_name].keys()))
        actual_type = actual_properties[prop_name]["type"]
        
        if expected_type == actual_type:
            results["matching_properties"].append(prop_name)
            
            # For select properties, check options
            if expected_type == "select" and "options" in expected_properties[prop_name]["select"]:
                expected_options = {opt["name"]: opt.get("color") for opt in expected_properties[prop_name]["select"]["options"]}
                actual_options = {opt["name"]: opt.get("color") for opt in actual_properties[prop_name]["select"]["options"]}
                
                missing_options = []
                for opt_name, color in expected_options.items():
                    if opt_name not in actual_options:
                        missing_options.append({"name": opt_name, "color": color})
                    elif color != actual_options[opt_name]:
                        missing_options.append({"name": opt_name, "expected_color": color, "actual_color": actual_options[opt_name]})
                
                extra_options = [{"name": name, "color": color} for name, color in actual_options.items() 
                                if name not in expected_options]
                
                if missing_options or extra_options:
                    results["select_option_differences"][prop_name] = {
                        "missing_options": missing_options,
                        "extra_options": extra_options
                    }
        else:
            results["type_mismatches"].append({
                "property": prop_name,
                "expected_type": expected_type,
                "actual_type": actual_type
            })
            
    return results

def generate_config_update_script(database_id: str, actual_properties: Dict[str, Any]) -> str:
    """
    Generate Python code to update the config based on actual database properties
    
    Args:
        database_id: The Notion database ID
        actual_properties: The actual properties from the database
        
    Returns:
        str: Python code that can update the config
    """
    code = [
        "# Updated NOTION_CONFIG based on actual database properties",
        "NOTION_CONFIG = {",
        f'    "database_id": "{database_id}",',
        '    "database_properties": {'
    ]
    
    for prop_name, prop_data in actual_properties.items():
        prop_type = prop_data["type"]
        
        if prop_type == "title":
            code.append(f'        "{prop_name}": {{"title": {{}}}},')
        elif prop_type == "rich_text":
            code.append(f'        "{prop_name}": {{"rich_text": {{}}}},')
        elif prop_type == "select":
            options_code = []
            for option in prop_data["select"]["options"]:
                opt_name = option["name"]
                opt_color = option.get("color", "default")
                options_code.append(f'                    {{"name": "{opt_name}", "color": "{opt_color}"}}')
            
            options_str = ",\n".join(options_code)
            code.append(f'        "{prop_name}": {{')
            code.append(f'            "select": {{')
            code.append(f'                "options": [')
            code.append(options_str)
            code.append(f'                ]')
            code.append(f'            }}')
            code.append(f'        }},')
        elif prop_type == "multi_select":
            options_code = []
            for option in prop_data["multi_select"]["options"]:
                opt_name = option["name"]
                opt_color = option.get("color", "default")
                options_code.append(f'                    {{"name": "{opt_name}", "color": "{opt_color}"}}')
            
            options_str = ",\n".join(options_code)
            code.append(f'        "{prop_name}": {{')
            code.append(f'            "multi_select": {{')
            code.append(f'                "options": [')
            code.append(options_str)
            code.append(f'                ]')
            code.append(f'            }}')
            code.append(f'        }},')
        elif prop_type == "date":
            code.append(f'        "{prop_name}": {{"date": {{}}}},')
        elif prop_type == "people":
            code.append(f'        "{prop_name}": {{"people": {{}}}},')
        elif prop_type == "checkbox":
            code.append(f'        "{prop_name}": {{"checkbox": {{}}}},')
        elif prop_type == "url":
            code.append(f'        "{prop_name}": {{"url": {{}}}},')
        elif prop_type == "email":
            code.append(f'        "{prop_name}": {{"email": {{}}}},')
        elif prop_type == "phone_number":
            code.append(f'        "{prop_name}": {{"phone_number": {{}}}},')
        elif prop_type == "number":
            format_str = prop_data["number"].get("format", "number")
            code.append(f'        "{prop_name}": {{"number": {{"format": "{format_str}"}}}},')
        else:
            # Generic fallback for other property types
            code.append(f'        "{prop_name}": {{"{prop_type}": {{}}}},')
    
    # Close the dictionaries
    code.append('    }')
    code.append('}')
    
    return "\n".join(code)

def main():
    print("============================================")
    print("   NOTION DATABASE PROPERTY TYPE CHECKER")
    print("============================================")
    
    # Get Notion token
    notion_token = os.environ.get("NOTION_TOKEN")
    if not notion_token:
        notion_token = input("Enter your Notion API token: ")
    
    if not notion_token:
        print("❌ No token provided. Exiting.")
        exit(1)
    
    # Get database ID
    database_id = input("Enter your Notion database ID: ")
    if not database_id:
        print("❌ No database ID provided. Exiting.")
        exit(1)
    
    # Get database properties
    print(f"\nFetching properties for database {database_id}...")
    properties = get_database_properties(notion_token, database_id)
    
    if not properties:
        print("❌ Failed to retrieve database properties.")
        exit(1)
    
    # Save actual properties to file for reference
    with open("actual_notion_properties.json", "w") as f:
        json.dump(properties, f, indent=2)
    print("✅ Saved actual properties to 'actual_notion_properties.json'")
    
    # Compare with expected config
    print("\nComparing with expected configuration...")
    comparison = compare_properties(properties, NOTION_CONFIG)
    
    # Print comparison results
    print("\n============= COMPARISON RESULTS =============")
    
    print(f"\n✅ Matching Properties: {len(comparison['matching_properties'])}")
    for prop in comparison['matching_properties']:
        print(f"   - {prop}")
    
    if comparison['type_mismatches']:
        print(f"\n⚠️ Type Mismatches: {len(comparison['type_mismatches'])}")
        for mismatch in comparison['type_mismatches']:
            print(f"   - {mismatch['property']}: Expected '{mismatch['expected_type']}', got '{mismatch['actual_type']}'")
    
    if comparison['missing_in_db']:
        print(f"\n❌ Properties in config but missing in database: {len(comparison['missing_in_db'])}")
        for prop in comparison['missing_in_db']:
            print(f"   - {prop}")
    
    if comparison['extra_in_db']:
        print(f"\n⚠️ Extra properties in database not in config: {len(comparison['extra_in_db'])}")
        for prop in comparison['extra_in_db']:
            print(f"   - {prop}")
    
    if comparison['select_option_differences']:
        print(f"\n⚠️ Select Option Differences:")
        for prop, diff in comparison['select_option_differences'].items():
            print(f"   - {prop}:")
            if diff['missing_options']:
                print(f"     Missing options in database: {len(diff['missing_options'])}")
                for opt in diff['missing_options']:
                    if 'expected_color' in opt:
                        print(f"       • {opt['name']}: Expected color '{opt['expected_color']}', got '{opt['actual_color']}'")
                    else:
                        print(f"       • {opt['name']} (color: {opt['color']})")
            
            if diff['extra_options']:
                print(f"     Extra options in database: {len(diff['extra_options'])}")
                for opt in diff['extra_options']:
                    print(f"       • {opt['name']} (color: {opt['color']})")
    
    # Generate updated config
    print("\n============= SUGGESTED CONFIG UPDATE =============")
    updated_config = generate_config_update_script(database_id, properties)
    print(updated_config)
    
    # Save suggested config to file
    with open("suggested_notion_config.py", "w") as f:
        f.write(updated_config)
    print("\n✅ Saved suggested config to 'suggested_notion_config.py'")
    
    print("\n============= NEXT STEPS =============")
    print("1. Review the comparison results above")
    print("2. Check 'suggested_notion_config.py' for an updated config based on actual database")
    print("3. Update your Task classes if needed to match the actual options in the database")
    print("4. Modify your database in Notion or update your config as needed to resolve differences")

if __name__ == "__main__":
    main()