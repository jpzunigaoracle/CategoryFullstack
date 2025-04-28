
import csv
from typing import List


def read_messages(filepath: str) -> List[dict]:
    """Reads all complaints from the CSV file."""
    try:
        with open(filepath, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Get the actual column names from the CSV
            fieldnames = reader.fieldnames
            
            # Define possible mappings for column names
            column_mappings = {
                'id': ['DialogID', 'Dialog_ID', 'ID', 'Id'],
                'complaint': ['CustomerComplaintDialog', 'Customer_Complaint_Dialog', 'Complaint', 'Dialog'],
                'created': ['Date&TimeCreated', 'DateTimeCreated', 'Created', 'StartTime'],
                'ended': ['Date&TimeEnded', 'DateTimeEnded', 'Ended', 'EndTime']
            }
            
            # Find the actual column names in the CSV
            actual_columns = {}
            for key, possible_names in column_mappings.items():
                found_column = next((col for col in possible_names if col in fieldnames), None)
                if not found_column:
                    raise ValueError(f"Could not find a matching column for {key} in the CSV file")
                actual_columns[key] = found_column
            
            messages = []
            for row in reader:
                try:
                    message = {
                        "id": row[actual_columns['id']],
                        "Customer Complaint Dialog": row[actual_columns['complaint']],
                        "Date & Time Created": row[actual_columns['created']],
                        "Date & Time Ended": row[actual_columns['ended']],
                        "original_complaint": row[actual_columns['complaint']]
                    }
                    messages.append(message)
                except KeyError as e:
                    print(f"Warning: Skipping row due to missing data: {e}")
                    continue
                
        if not messages:
            raise ValueError("No valid messages were read from the CSV file")
            
        return messages
    except Exception as e:
        print(f"Error reading CSV file: {e}")
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
