import requests
import os
import json
from datetime import datetime

def check_notion_access(notion_token):
    """
    Comprehensive check of what's accessible via your Notion API token.
    
    Args:
        notion_token (str): Your Notion integration token
        
    Returns:
        dict: Summary of accessible content
    """
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # First, verify the token works at all with a simple users endpoint
    print("Step 1: Verifying API token...")
    try:
        user_response = requests.get("https://api.notion.com/v1/users", headers=headers)
        if user_response.status_code == 200:
            print("✅ Authentication successful!")
            users = user_response.json()["results"]
            print(f"   Found {len(users)} users associated with this integration.")
        else:
            print(f"❌ Authentication failed! Status code: {user_response.status_code}")
            print(f"   Error message: {user_response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return None
    
    # Now search for ALL content (not filtering by type)
    print("\nStep 2: Searching for ALL accessible content...")
    search_url = "https://api.notion.com/v1/search"
    
    all_results = []
    start_cursor = None
    
    # Paginate through all results
    while True:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor
            
        try:
            response = requests.post(search_url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"❌ Search failed with status code: {response.status_code}")
                print(f"   Error: {response.text}")
                break
                
            result_data = response.json()
            results = result_data.get("results", [])
            all_results.extend(results)
            
            if result_data.get("has_more", False) and result_data.get("next_cursor"):
                start_cursor = result_data["next_cursor"]
                print(f"   Found {len(results)} items, continuing to next page...")
            else:
                break
                
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            break
    
    print(f"\nFound {len(all_results)} total items. Analyzing content types...")
    
    # Analyze what types of content we found
    content_summary = {
        "total_items": len(all_results),
        "databases": [],
        "pages": [],
        "other": []
    }
    
    for item in all_results:
        object_type = item.get("object", "unknown")
        
        if object_type == "database":
            title = get_title(item)
            content_summary["databases"].append({
                "id": item["id"],
                "title": title,
                "url": item.get("url", ""),
                "created_time": item.get("created_time", ""),
                "properties": list(item.get("properties", {}).keys())
            })
        elif object_type == "page":
            title = get_page_title(item)
            content_summary["pages"].append({
                "id": item["id"],
                "title": title,
                "url": item.get("url", ""),
                "created_time": item.get("created_time", ""),
                "parent_type": item.get("parent", {}).get("type", "unknown")
            })
        else:
            content_summary["other"].append({
                "id": item["id"],
                "object_type": object_type
            })
    
    return content_summary

def get_title(db):
    """Extract the title from a database object"""
    if "title" in db and db["title"]:
        title_parts = [text_content.get("text", {}).get("content", "") 
                      for text_content in db["title"]]
        return "".join(title_parts)
    return "Untitled"

def get_page_title(page):
    """Extract title from a page object"""
    if "properties" in page and "title" in page["properties"]:
        title_property = page["properties"]["title"]
        if "title" in title_property and title_property["title"]:
            title_parts = [text_content.get("text", {}).get("content", "") 
                          for text_content in title_property["title"]]
            return "".join(title_parts)
    return "Untitled Page"

def save_results_to_file(content_summary):
    """Save results to a JSON file for inspection"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"notion_content_summary_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(content_summary, f, indent=2)
    
    return filename

if __name__ == "__main__":
    print("============================================")
    print("     NOTION API ACCESS CHECKER v1.0")
    print("============================================")
    
    # Get Notion token
    notion_token = os.environ.get("NOTION_TOKEN")
    if not notion_token:
        notion_token = input("Enter your Notion API token: ")
    
    if not notion_token:
        print("❌ No token provided. Exiting.")
        exit(1)
    
    # Run the check
    content_summary = check_notion_access(notion_token)
    
    if not content_summary:
        print("\n❌ Failed to access Notion API. Please verify your token and try again.")
        exit(1)
    
    # Print summary
    print("\n============= RESULTS SUMMARY =============")
    print(f"Total accessible items: {content_summary['total_items']}")
    print(f"Databases: {len(content_summary['databases'])}")
    print(f"Pages: {len(content_summary['pages'])}")
    print(f"Other objects: {len(content_summary['other'])}")
    
    # Save full results to file
    filename = save_results_to_file(content_summary)
    print(f"\nDetailed results saved to: {filename}")
    
    # Display databases if any
    if content_summary['databases']:
        print("\n============= DATABASES =============")
        for i, db in enumerate(content_summary['databases'], 1):
            print(f"\n{i}. {db['title']}")
            print(f"   ID: {db['id']}")
            print(f"   URL: {db['url']}")
            print(f"   Properties: {', '.join(db['properties'])}")
    else:
        print("\n⚠️ NO DATABASES FOUND. This could mean:")
        print("  1. Your integration doesn't have access to any databases")
        print("  2. You need to explicitly share databases with your integration")
        
    # Display a few pages as example
    if content_summary['pages']:
        print("\n============= SOME PAGES =============")
        for i, page in enumerate(content_summary['pages'][:5], 1):
            print(f"\n{i}. {page['title']}")
            print(f"   ID: {page['id']}")
            print(f"   URL: {page['url']}")
            print(f"   Parent type: {page['parent_type']}")
        
        if len(content_summary['pages']) > 5:
            print(f"\n   ... and {len(content_summary['pages']) - 5} more pages (see JSON file)")
    
    print("\n============= TROUBLESHOOTING =============")
    print("If you're not seeing expected content:")
    print("1. Verify you've shared pages/databases with your integration")
    print("   - Go to the page in Notion")
    print("   - Click '...' in the top right")
    print("   - Select 'Add connections'")
    print("   - Find and add your integration")
    print("2. Check integration permissions")
    print("   - Go to https://www.notion.so/my-integrations")
    print("   - Select your integration")
    print("   - Verify it has the necessary capabilities (Read Content, etc.)")