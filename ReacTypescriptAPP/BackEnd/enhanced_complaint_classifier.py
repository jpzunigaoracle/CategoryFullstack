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
    # Definitions if import fails
    MODEL_REGISTRY = {
        "cohere_oci": {
            "service_endpoint": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
            "model_id": "cohere.command",
            "model_kwargs": {
                "temperature": 0.7,
                "max_tokens": 1500
            }
        }
    }
    
    # Two-step classification prompts with stronger emphasis on creating 8 categories
    CATEGORY_CREATION_PROMPT = """You are an expert complaint classifier for SMEG appliances. Your task is to:

1. Read all the customer complaint summaries provided in the input
2. Create EXACTLY 8 distinct complaint categories that best represent all the complaints
3. Return ONLY these 8 categories in a JSON array format

IMPORTANT: You MUST create exactly 8 categories based on the actual complaint data. Do not use generic categories unless they truly represent the data.

The categories should be comprehensive and cover all types of complaints in the dataset.
Return your analysis in this EXACT JSON format:
{
  "categories": ["Category1", "Category2", "Category3", "Category4", "Category5", "Category6", "Category7", "Category8"]
}"""

    COMPLAINT_CLASSIFICATION_PROMPT = """You are an expert complaint classifier for SMEG appliances. Your task is to:

1. Use the 8 predefined categories provided
2. Assign each complaint to exactly one of these 8 categories based on the complaint summary
3. Return the original data with the new category classification added

Categories: {categories}

Return your analysis in this EXACT JSON format with all complaints classified."""

    PROMPT_SETS = {
        "cohere_oci": {
            "category_creation": CATEGORY_CREATION_PROMPT,
            "complaint_classification": COMPLAINT_CLASSIFICATION_PROMPT
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
                
            # Two-step classification process
            # Step 1: Create 8 categories based on all complaints
            categories = create_categories(complaints)
            
            # Step 2: Classify each complaint into one of these categories
            classified_data = classify_complaints_with_categories(complaints, categories)
            
            # Return the classified data directly to match the expected format
            return classified_data
            
        except Exception as e:
            print(f"Error fetching first stage data: {str(e)}", file=sys.stderr)
            # Return error message
            return {"error": f"Failed to fetch first stage data: {str(e)}"}
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return {"error": f"Failed to classify complaints: {str(e)}"}

def create_categories(complaints):
    """
    Step 1: Create exactly 8 categories based on all complaint summaries
    This function will retry multiple times to ensure AI generates the categories
    """
    # Format complaints for the AI model - we only need summaries for category creation
    summaries = []
    for complaint in complaints:
        if "summary" in complaint:
            summaries.append(complaint["summary"])
    
    formatted_summaries = json.dumps(summaries, indent=2)
    
    # Use Cohere model by default
    model_name = "cohere_oci"
    model_config = MODEL_REGISTRY[model_name]
    
    # Get the prompt for category creation
    prompt = get_prompt(model_name, "category_creation")
    
    # Check if API key is available
    api_key = os.environ.get('OCI_API_KEY')
    if not api_key:
        print("Error: OCI_API_KEY environment variable not set.", file=sys.stderr)
        raise Exception("OCI_API_KEY environment variable not set. Cannot generate categories without API access.")
    
    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # We'll try multiple times with different temperatures if needed
    temperatures = [0.7, 0.5, 0.3, 0.9]
    max_retries = len(temperatures)
    
    for retry_count, temperature in enumerate(temperatures):
        try:
            payload = {
                "prompt": prompt,
                "inputs": [formatted_summaries],
                "temperature": temperature,
                "max_tokens": model_config["model_kwargs"]["max_tokens"]
            }
            
            # Make the API request to OCI AI
            response = requests.post(
                f"{model_config['service_endpoint']}/inference/{model_config['model_id']}",
                headers=headers,
                json=payload,
                timeout=30  # Add timeout to prevent hanging
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse the AI response which should be in JSON format
                ai_response = result.get("generated_text", "")
                
                try:
                    # The AI should return a JSON string with categories
                    categories_data = json.loads(ai_response)
                    
                    # Validate that we have exactly 8 categories
                    if "categories" in categories_data and len(categories_data["categories"]) == 8:
                        print(f"Successfully generated 8 categories on attempt {retry_count+1}", file=sys.stderr)
                        return categories_data["categories"]
                    else:
                        print(f"Attempt {retry_count+1}: AI did not return exactly 8 categories", file=sys.stderr)
                        # If we have some categories but not 8, and this is our last retry
                        if "categories" in categories_data and len(categories_data["categories"]) > 0 and retry_count == max_retries - 1:
                            # Take first 8 or pad to 8 with generic categories
                            categories = categories_data["categories"][:8]
                            while len(categories) < 8:
                                categories.append(f"Category {len(categories)+1}")
                            return categories
                except json.JSONDecodeError as e:
                    print(f"Attempt {retry_count+1}: Error parsing AI response: {e}", file=sys.stderr)
                    # Try to extract categories from the text if possible
                    import re
                    categories = re.findall(r'"([^"]+)"', ai_response)
                    if len(categories) >= 8 and retry_count == max_retries - 1:
                        return categories[:8]
            else:
                print(f"Attempt {retry_count+1}: API Error: {response.status_code} - {response.text}", file=sys.stderr)
                
            # If this was the last retry and we still don't have categories, raise an exception
            if retry_count == max_retries - 1:
                raise Exception("Failed to generate categories after multiple attempts")
                
        except Exception as e:
            # If this is the last retry, re-raise the exception
            if retry_count == max_retries - 1:
                print(f"All attempts to generate categories failed: {str(e)}", file=sys.stderr)
                raise Exception(f"Failed to generate categories: {str(e)}")
            else:
                print(f"Attempt {retry_count+1} failed: {str(e)}. Retrying...", file=sys.stderr)

def classify_complaints_with_categories(complaints, categories):
    """
    Step 2: Classify each complaint into one of the predefined categories
    """
    # Format complaints for the AI model
    formatted_complaints = json.dumps(complaints, indent=2)
    
    # Use Cohere model by default
    model_name = "cohere_oci"
    model_config = MODEL_REGISTRY[model_name]
    
    # Get the prompt for complaint classification and insert the categories
    prompt_template = get_prompt(model_name, "complaint_classification")
    prompt = prompt_template.format(categories=json.dumps(categories))
    
    # Check if API key is available
    api_key = os.environ.get('OCI_API_KEY')
    if not api_key:
        print("Error: OCI_API_KEY environment variable not set.", file=sys.stderr)
        raise Exception("OCI_API_KEY environment variable not set. Cannot classify complaints without API access.")
    
    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # We'll try multiple times with different temperatures if needed
    temperatures = [0.7, 0.5, 0.3, 0.9]
    max_retries = len(temperatures)
    
    for retry_count, temperature in enumerate(temperatures):
        try:
            payload = {
                "prompt": prompt,
                "inputs": [formatted_complaints],
                "temperature": temperature,
                "max_tokens": model_config["model_kwargs"]["max_tokens"]
            }
            
            # Make the API request to OCI AI
            response = requests.post(
                f"{model_config['service_endpoint']}/inference/{model_config['model_id']}",
                headers=headers,
                json=payload,
                timeout=30  # Add timeout to prevent hanging
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse the AI response which should be in JSON format
                ai_response = result.get("generated_text", "")
                
                try:
                    # The AI should return a JSON string with classified complaints
                    classified_data = json.loads(ai_response)
                    
                    # Ensure all complaints have a classification
                    if "classified_complaints" in classified_data:
                        # Validate that all complaints have a complaint_type
                        for complaint in classified_data["classified_complaints"]:
                            if "complaint_type" not in complaint:
                                # Assign a default category from our list
                                complaint["complaint_type"] = categories[0]
                        
                        # Ensure the categories field is present
                        if "categories" not in classified_data:
                            classified_data["categories"] = categories
                        
                        print(f"Successfully classified complaints on attempt {retry_count+1}", file=sys.stderr)
                        return classified_data
                    else:
                        print(f"Attempt {retry_count+1}: AI response missing classified_complaints", file=sys.stderr)
                except json.JSONDecodeError as e:
                    print(f"Attempt {retry_count+1}: Error parsing AI response: {e}", file=sys.stderr)
            else:
                print(f"Attempt {retry_count+1}: API Error: {response.status_code} - {response.text}", file=sys.stderr)
                
            # If this was the last retry and we still don't have classifications, raise an exception
            if retry_count == max_retries - 1:
                raise Exception("Failed to classify complaints after multiple attempts")
                
        except Exception as e:
            # If this is the last retry, re-raise the exception
            if retry_count == max_retries - 1:
                print(f"All attempts to classify complaints failed: {str(e)}", file=sys.stderr)
                raise Exception(f"Failed to classify complaints: {str(e)}")
            else:
                print(f"Attempt {retry_count+1} failed: {str(e)}. Retrying...", file=sys.stderr)

def get_classified_complaints():
    """API endpoint function to get classified complaints"""
    result = classify_complaints()
    return result

if __name__ == "__main__":
    # Run the classification and print the result
    result = classify_complaints()
    print(json.dumps(result))