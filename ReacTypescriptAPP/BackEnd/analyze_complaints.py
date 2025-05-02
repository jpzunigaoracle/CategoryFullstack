
import json
import sys
import os
import requests
from datetime import datetime

# Add the current directory to the path to make local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import from local utils directory
try:
    from utils.llm_configM import MODEL_REGISTRY, get_prompt
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback definitions if import fails
    MODEL_REGISTRY = {
        "cohere_oci": {
            "service_endpoint": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
            "model_id": "cohere.command",
            "model_kwargs": {
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }
    }
    
    def get_prompt(model_name, prompt_type):
        # Fallback prompt for summarization
        if prompt_type == "summarization":
            return """You are an expert complaint analyzer. Your task is to:

1. Read each customer complaint dialog provided in the input
2. For EACH complaint, create a short summary (1-2 sentences)
3. For EACH complaint, assign a sentiment score from 1-10 (1=very negative, 10=very positive)
4. Include the date and time created and date and time ended for each complaint

Return your analysis in this EXACT JSON format:
[
  {
    "id": "1",
    "summary": "Customer's fridge is not cooling properly and needs warranty service.",
    "sentiment_score": 3,
    "date_created": "2023-01-10",
    "time_created": "9:30 AM",
    "date_ended": "2023-01-10",
    "time_ended": "9:45 AM"
  },
  ... and so on for each complaint
]"""
        return ""

def generate_report():
    """
    Generate a report of analyzed complaints with sentiment scores using OCI AI.
    Returns data in the specified format.
    """
    try:
        # Read complaints from JSON file
        complaints_path = os.path.join(os.path.dirname(__file__), 'ComplainsList.json')
        
        with open(complaints_path, 'r', encoding='utf-8') as f:
            complaints = json.load(f)
        
        # Format complaints for the AI model
        formatted_complaints = format_complaints_for_ai(complaints)
        
        # Use OCI AI to analyze the complaints
        analyzed_complaints = analyze_with_oci_ai(formatted_complaints)
        
        # Format the response as requested
        response = {
            "generate_report": {
                "reports": [analyzed_complaints]
            }
        }
        
        return response
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return {"error": f"Failed to process complaints: {str(e)}"}

def format_complaints_for_ai(complaints):
    """Format the complaints data for sending to the AI model"""
    formatted_text = "Customer Complaints to Analyze:\n\n"
    
    for complaint in complaints:
        formatted_text += f"Complaint ID: {complaint['DialogID']}\n"
        formatted_text += f"Date Created: {complaint['DateCreated']}\n"
        formatted_text += f"Time Created: {complaint['Date&TimeCreated']}\n"
        formatted_text += f"Date Ended: {complaint['DateEnded']}\n"
        formatted_text += f"Time Ended: {complaint['Date&TimeEnded']}\n"
        formatted_text += f"Dialog: {complaint['CustomerComplaintDialog']}\n\n"
    
    return formatted_text, complaints  # Return the original complaints as well

def analyze_with_oci_ai(complaints_data):
    """
    Use OCI AI to analyze the complaints
    """
    complaints_text, original_complaints = complaints_data
    # Use Cohere model by default
    model_name = "cohere_oci"
    model_config = MODEL_REGISTRY[model_name]
    
    # Get the prompt for summarization
    prompt = get_prompt(model_name, "summarization")
    
    # Check if API key is available
    api_key = os.environ.get('OCI_API_KEY')
    if not api_key:
        print("Warning: OCI_API_KEY environment variable not set. Using fallback analysis.", file=sys.stderr)
        return fallback_analysis(complaints_text)
    
    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "prompt": prompt,
        "inputs": [complaints_text],
        "temperature": model_config["model_kwargs"]["temperature"],
        "max_tokens": model_config["model_kwargs"]["max_tokens"]
    }
    
    # Make the API request to OCI AI
    try:
        response = requests.post(
            f"{model_config['service_endpoint']}/inference/{model_config['model_id']}",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            # Parse the AI response which should be in JSON format
            ai_response = result.get("generated_text", "")
            
            try:
                # The AI should return a JSON string, parse it
                analyzed_complaints = json.loads(ai_response)
                
                # Ensure all IDs are integers to match the expected format
                for complaint in analyzed_complaints:
                    if "id" in complaint and isinstance(complaint["id"], str):
                        try:
                            complaint["id"] = int(complaint["id"])
                        except ValueError:
                            # Keep as string if conversion fails
                            pass
                
                return analyzed_complaints
            except json.JSONDecodeError as e:
                print(f"Error parsing AI response: {e}", file=sys.stderr)
                print(f"Raw AI response: {ai_response}", file=sys.stderr)
                return fallback_analysis(complaints_text)
        else:
            print(f"API Error: {response.status_code} - {response.text}", file=sys.stderr)
            # Fallback to simple analysis if API fails
            return fallback_analysis(complaints_text)
    except Exception as e:
        print(f"Error calling OCI AI: {str(e)}", file=sys.stderr)
        # Fallback to simple analysis if API fails
        return fallback_analysis(complaints_text)

def fallback_analysis(complaints_data):
    """Fallback method if the API call fails"""
    # Extract complaint IDs and basic info
    import re
    
    # Handle both cases - when complaints_data is a tuple or just a string
    if isinstance(complaints_data, tuple) and len(complaints_data) == 2:
        complaints_text, original_complaints = complaints_data
    else:
        # If it's just a string, use it directly and set original_complaints to empty list
        complaints_text = complaints_data
        original_complaints = []
    
    complaints = []
    complaint_blocks = re.split(r'Complaint ID:', complaints_text)[1:]
    
    for i, block in enumerate(complaint_blocks):
        lines = block.strip().split('\n')
        complaint_id = lines[0].strip()
        
        # Extract dates and times
        date_created = re.search(r'Date Created: (.*)', block)
        date_created = date_created.group(1) if date_created else ""
        
        time_created = re.search(r'Time Created: (.*)', block)
        time_created = time_created.group(1) if time_created else ""
        
        date_ended = re.search(r'Date Ended: (.*)', block)
        date_ended = date_ended.group(1) if date_ended else ""
        
        time_ended = re.search(r'Time Ended: (.*)', block)
        time_ended = time_ended.group(1) if time_ended else ""
        
        # Extract dialog
        dialog = re.search(r'Dialog: (.*)', block, re.DOTALL)
        dialog_text = dialog.group(1).strip() if dialog else ""
        
        # Simple summary - first sentence of customer part
        customer_part = dialog_text.split('<br>')[0] if dialog_text else ""
        if customer_part.startswith("C: "):
            customer_part = customer_part[3:]
        summary = customer_part.split('.')[0] + "."
        
        # Simple sentiment score (neutral by default)
        sentiment_score = 5
        
        # Try to convert complaint_id to integer
        try:
            complaint_id_int = int(complaint_id)
        except ValueError:
            complaint_id_int = i + 1  # Fallback to index + 1
        
        # Add the original dialog
        original_dialog = ""
        if i < len(original_complaints):
            original_dialog = original_complaints[i]["CustomerComplaintDialog"]
        
        complaints.append({
            "id": complaint_id_int,
            "summary": summary,
            "sentiment_score": sentiment_score,
            "date_created": date_created,
            "time_created": time_created,
            "date_ended": date_ended,
            "time_ended": time_ended,
            "original_dialog": original_dialog
        })
    
    return complaints

if __name__ == "__main__":
    # Generate the report
    report = generate_report()
    
    # Print the report as JSON
    print(json.dumps(report))
  