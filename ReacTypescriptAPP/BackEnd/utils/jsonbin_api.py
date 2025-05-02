"""
Utility module for interacting with JSONBin.io API
"""
import requests
import json

# Hardcoded credentials (NOT RECOMMENDED for production)
API_KEY = "$2a$10$AEUUU8hwn3zGMJImX3oZPuIMwRkKrMIHqpo3rQxDc/Z4XJzhp3ece"
BIN_ID = "68148e5c8561e97a500c2bfc"

def fetch_complaints():
    """
    Fetch complaints data from JSONBin.io
    Returns the complaints data as a list of dictionaries
    """
    url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    
    headers = {
        "X-Master-Key": API_KEY,
        "X-Bin-Meta": "false"  # Don't include metadata in the response
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # The response contains the JSON data
            return response.json()
        else:
            print(f"JSONBin.io API Error: {response.status_code} - {response.text}")
            raise Exception(f"Failed to fetch data from JSONBin.io: {response.status_code}")
    except Exception as e:
        print(f"Error fetching data from JSONBin.io: {str(e)}")
        raise