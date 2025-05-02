
import json
from typing import List


def read_messages(filepath: str) -> List[dict]:
    """Reads all complaints from the JSON file."""
    try:
        with open(filepath, encoding='utf-8') as file:
            data = json.load(file)
            
            messages = []
            for item in data:
                try:
                    # Make sure the ID is being preserved correctly
                    message = {
                        "id": item["DialogID"],  # This should be the original DialogID from the JSON
                        "Customer Complaint Dialog": item["CustomerComplaintDialog"],
                        "date_created": item.get("DateCreated", ""),
                        "time_created": item.get("Date&TimeCreated", ""),
                        "date_ended": item.get("DateEnded", ""),
                        "time_ended": item.get("Date&TimeEnded", ""),
                        "original_complaint": item["CustomerComplaintDialog"]
                    }
                    messages.append(message)
                except KeyError as e:
                    print(f"Warning: Skipping item due to missing data: {e}")
                    continue
                
        if not messages:
            raise ValueError("No valid messages were read from the JSON file")
            
        return messages
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        # Return an empty list instead of None to prevent further errors
        return []

def match_categories(summaries, categories):
    result = []
    if not summaries or not categories or not summaries[0] or not categories[0]:
        return result
        
    # Extract the assigned categories from the summarization step
    for elem in summaries[0]:
        if isinstance(elem, dict) and "assigned_category" in elem:
            # The category is already assigned in the summarization step
            result.append(elem)
        else:
            # If somehow the category wasn't assigned, add a default
            elem["assigned_category"] = "Uncategorized"
            result.append(elem)
    
    return result


def group_by_category_level(categories_list):
    """
    Groups a list of category dictionaries by their hierarchical levels.
    
    Args:
        categories_list (list): List of dictionaries with category information
        
    Returns:
        dict: A nested dictionary organized by primary, secondary, and tertiary categories
    """
    result = {}
    
    for category in categories_list:
        primary = category["primary_category"]
        secondary = category["secondary_category"]
        tertiary = category["tertiary_category"]
        
        # Initialize primary category if it doesn't exist
        if primary not in result:
            result[primary] = {}
        
        # Initialize secondary category if it doesn't exist
        if secondary not in result[primary]:
            result[primary][secondary] = {}
        
        # Add message ID to the tertiary category
        if tertiary not in result[primary][secondary]:
            result[primary][secondary][tertiary] = []
        
        result[primary][secondary][tertiary].append(category["id"])
    
    return result
