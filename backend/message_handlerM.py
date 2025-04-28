
import csv
from typing import List


def read_messages(filepath: str, columns: List[str]= ["ID", "Message"]) -> List[List[str]]:
    """Reads a CSV file and returns specific columns as a list of lists."""
    with open(filepath, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # Using DictReader for column name-based access
        extracted_data = []
        
        # Iterate over each row and extract specified columns
        for row in reader:
            extracted_row = [row[col] for col in columns if col in row]
            extracted_data.append(extracted_row)
    
    return extracted_data

def match_categories(summaries, categories):
    result = []
    for i, elem in enumerate(summaries[0]):
        if elem["id"] == categories[0][i]["id"]:
            elem["primary_category"] = categories[0][i]["primary_category"]
            elem["secondary_category"] = categories[0][i]["secondary_category"]
            elem["tertiary_category"] = categories[0][i]["tertiary_category"]
            print(i)
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
