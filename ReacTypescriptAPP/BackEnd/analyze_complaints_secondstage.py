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
    from utils.llm_configM import MODEL_REGISTRY
    from utils.promptsSecondStage import PROMPT_SETS
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
    
    # Fallback prompt for classification
    CLASSIFICATION_PROMPT = """You are an expert complaint classifier for SMEG appliances. Your task is to:

1. Read all the customer complaint summaries provided in the input
2. Create exactly 8 distinct complaint categories that best represent all the complaints
3. Assign each complaint to one of these 8 categories
4. Return the original data with the new category classification added

Return your analysis in this EXACT JSON format with 8 categories and all complaints classified."""

    PROMPT_SETS = {
        "cohere_oci": {
            "classification": CLASSIFICATION_PROMPT
        }
    }

def get_prompt(model_name, prompt_type):
    """Get the appropriate prompt for the model and prompt type"""
    if model_name not in PROMPT_SETS:
        raise ValueError(f"No prompts defined for model {model_name}")
    
    model_prompts = PROMPT_SETS[model_name]
    
    if prompt_type not in model_prompts:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    return model_prompts[prompt_type]

def classify_complaints():
    """
    Fetch the analyzed complaints from the first stage and classify them into categories.
    Returns data with complaint types added.
    """
    try:
        # Fetch the analyzed complaints from the first stage endpoint
        first_stage_url = "http://localhost:5000/api/analyze-complaints"
        
        try:
            response = requests.get(first_stage_url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data from first stage: {response.status_code}")
            
            first_stage_data = response.json()
            
            # Extract the complaints from the first stage data
            if "generate_report" in first_stage_data and "reports" in first_stage_data["generate_report"]:
                complaints = first_stage_data["generate_report"]["reports"][0]
            else:
                complaints = first_stage_data  # Fallback if structure is different
                
            # Classify the complaints
            classified_data = classify_with_oci_ai(complaints)
            
            # Return the classified data directly to match the expected format
            return classified_data
            
        except Exception as e:
            print(f"Error fetching first stage data: {str(e)}", file=sys.stderr)
            # Fallback to local file if API call fails
            return {"error": f"Failed to fetch first stage data: {str(e)}"}
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return {"error": f"Failed to classify complaints: {str(e)}"}

def classify_with_oci_ai(complaints):
    """
    Use OCI AI to classify the complaints into categories
    """
    # Format complaints for the AI model
    formatted_complaints = json.dumps(complaints, indent=2)
    
    # Use Cohere model by default
    model_name = "cohere_oci"
    model_config = MODEL_REGISTRY[model_name]
    
    # Get the prompt for classification
    prompt = get_prompt(model_name, "classification")
    
    # Check if API key is available
    api_key = os.environ.get('OCI_API_KEY')
    if not api_key:
        print("Warning: OCI_API_KEY environment variable not set. Using fallback classification.", file=sys.stderr)
        return fallback_classification(complaints)
    
    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "prompt": prompt,
        "inputs": [formatted_complaints],
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
                classified_data = json.loads(ai_response)
                return classified_data
            except json.JSONDecodeError as e:
                print(f"Error parsing AI response: {e}", file=sys.stderr)
                print(f"Raw AI response: {ai_response}", file=sys.stderr)
                return fallback_classification(complaints)
        else:
            print(f"API Error: {response.status_code} - {response.text}", file=sys.stderr)
            # Fallback to simple classification if API fails
            return fallback_classification(complaints)
    except Exception as e:
        print(f"Error calling OCI AI: {str(e)}", file=sys.stderr)
        # Fallback to simple classification if API fails
        return fallback_classification(complaints)

def fallback_classification(complaints):
    """Fallback method if the API call fails"""
    # Create 8 default categories
    default_categories = [
        "Product Defect",
        "Delivery Issue",
        "Warranty Concern",
        "Account Problem",
        "Technical Support",
        "Service Request",
        "Billing Issue",
        "Product Information"
    ]
    
    # Simple classification based on keywords in the summary
    classified_complaints = []
    
    for complaint in complaints:
        summary = complaint.get("summary", "").lower()
        
        # Simple keyword matching for classification
        if any(word in summary for word in ["not working", "broken", "defect", "damage", "malfunction"]):
            complaint_type = "Product Defect"
        elif any(word in summary for word in ["deliver", "shipping", "package", "arrival"]):
            complaint_type = "Delivery Issue"
        elif any(word in summary for word in ["warranty", "guarantee", "coverage"]):
            complaint_type = "Warranty Concern"
        elif any(word in summary for word in ["account", "login", "password", "profile"]):
            complaint_type = "Account Problem"
        elif any(word in summary for word in ["connect", "app", "wifi", "update", "software"]):
            complaint_type = "Technical Support"
        elif any(word in summary for word in ["service", "technician", "repair", "fix"]):
            complaint_type = "Service Request"
        elif any(word in summary for word in ["charge", "payment", "refund", "price", "cost"]):
            complaint_type = "Billing Issue"
        else:
            complaint_type = "Product Information"
        
        # Add the complaint type to the complaint
        complaint_with_type = complaint.copy()
        complaint_with_type["complaint_type"] = complaint_type
        classified_complaints.append(complaint_with_type)
    
    return {
        "categories": default_categories,
        "classified_complaints": classified_complaints
    }

if __name__ == "__main__":
    # Run the classification and print the result
    result = classify_complaints()
    print(json.dumps(result))