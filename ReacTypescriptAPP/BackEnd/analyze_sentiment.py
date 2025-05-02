import json
import sys
import os
import argparse
import requests
from datetime import datetime

# Add the current directory to the path to make local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import from local utils directory if available
try:
    from utils.llm_configM import MODEL_REGISTRY
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    # Fallback definitions if import fails
    MODEL_REGISTRY = {
        "cohere_oci": {
            "service_endpoint": "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com",
            "model_id": "cohere.command-r-plus-08-2024",
            "model_kwargs": {
                "temperature": 0,
                "max_tokens": 1000
            }
        }
    }

def analyze_sentiment(text, model_name="cohere_oci"):
    """
    Analyze the sentiment of a text using OCI AI.
    
    Args:
        text (str): The text to analyze
        model_name (str): The model to use for analysis
        
    Returns:
        dict: Sentiment analysis results
    """
    # Get model configuration
    if model_name not in MODEL_REGISTRY:
        print(f"Model {model_name} not found in registry. Using cohere_oci.", file=sys.stderr)
        model_name = "cohere_oci"
    
    model_config = MODEL_REGISTRY[model_name]
    
    # Create a detailed prompt for sentiment analysis
    prompt = """You are an expert sentiment analyzer for customer service interactions. 
    
Your task is to analyze the following customer complaint or conversation and:

1. Determine the overall sentiment on a scale of 1-10 where:
   - 1-3: Very negative (customer is angry, frustrated, or disappointed)
   - 4-5: Somewhat negative (customer has concerns or mild frustration)
   - 6-7: Neutral to slightly positive (customer is calm or satisfied with resolution)
   - 8-10: Very positive (customer is happy, grateful, or impressed)

2. Identify the key emotional factors in the text (e.g., frustration with product, appreciation for service)

3. Determine if there are any urgent issues that require immediate attention

IMPORTANT: You MUST analyze the sentiment carefully and assign an appropriate score between 1-10 based on the content. DO NOT default to a neutral score of 5. Even subtle language should influence your scoring.

Return your analysis in this EXACT JSON format:
{
  "sentiment_score": 3,
  "sentiment_category": "Very negative",
  "key_emotions": ["frustration", "anger"],
  "urgent": true,
  "explanation": "The customer expresses significant frustration about their product issue and uses strong negative language."
}

Here is the text to analyze:
"""
    
    # Combine prompt with the text to analyze
    full_prompt = f"{prompt}\n\n{text}"
    
    # Check if API key is available
    api_key = os.environ.get('OCI_API_KEY')
    if not api_key:
        print("Warning: OCI_API_KEY environment variable not set. Using mock AI response.", file=sys.stderr)
        return mock_ai_sentiment_analysis(text)
    
    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "prompt": full_prompt,
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
                # Extract the JSON part from the response
                import re
                json_match = re.search(r'({.*})', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    sentiment_data = json.loads(json_str)
                    return sentiment_data
                else:
                    print("No JSON found in AI response", file=sys.stderr)
                    return mock_ai_sentiment_analysis(text)
            except json.JSONDecodeError as e:
                print(f"Error parsing AI response: {e}", file=sys.stderr)
                print(f"Raw AI response: {ai_response}", file=sys.stderr)
                return mock_ai_sentiment_analysis(text)
        else:
            print(f"API Error: {response.status_code} - {response.text}", file=sys.stderr)
            # Use mock AI response if API fails
            return mock_ai_sentiment_analysis(text)
    except Exception as e:
        print(f"Error calling OCI AI: {str(e)}", file=sys.stderr)
        # Use mock AI response if API fails
        return mock_ai_sentiment_analysis(text)

def mock_ai_sentiment_analysis(text):
    """
    Generate a mock AI sentiment analysis response that mimics what the AI would produce.
    This is more sophisticated than the simple fallback and tries to simulate AI reasoning.
    """
    text = text.lower()
    
    # Define sentiment indicators with weights
    very_negative = {
        "broken": 3, "defect": 3, "terrible": 3, "worst": 3, "angry": 3, "furious": 3,
        "outraged": 3, "disgusted": 3, "horrible": 3, "awful": 3, "never": 2,
        "unacceptable": 3, "ridiculous": 2, "waste": 2, "useless": 2, "refund": 2,
        "complaint": 2, "damaged": 3, "dangerous": 3, "faulty": 3, "disappointed": 2
    }
    
    somewhat_negative = {
        "not working": 2, "issue": 2, "problem": 2, "disappointed": 2, "frustrating": 2,
        "poor": 2, "complaint": 2, "error": 2, "fail": 2, "bad": 2, "wrong": 2,
        "unhappy": 2, "delay": 2, "difficult": 1, "concern": 1, "unfortunately": 1,
        "not satisfied": 2, "doesn't work": 2, "isn't working": 2, "inconvenience": 1
    }
    
    neutral = {
        "ok": 1, "okay": 1, "fine": 1, "average": 1, "acceptable": 1,
        "standard": 1, "normal": 1, "expected": 1, "typical": 1, "information": 1,
        "question": 1, "inquiry": 1, "wondering": 1, "how do i": 1, "can you": 1
    }
    
    somewhat_positive = {
        "good": 1, "nice": 1, "helpful": 1, "resolved": 1, "solution": 1,
        "fixed": 1, "working": 1, "better": 1, "improved": 1, "satisfied": 1,
        "thank": 1, "appreciate": 1, "pleased": 1, "glad": 1, "happy with": 1
    }
    
    very_positive = {
        "excellent": 2, "amazing": 2, "outstanding": 2, "fantastic": 2, "wonderful": 2,
        "great": 2, "perfect": 2, "love": 2, "best": 2, "exceptional": 2,
        "brilliant": 2, "superb": 2, "delighted": 2, "thrilled": 2, "thank you so much": 3,
        "extremely satisfied": 3, "incredibly helpful": 3, "exceeded expectations": 3
    }
    
    # Calculate weighted scores
    very_neg_score = sum(weight for word, weight in very_negative.items() if word in text)
    somewhat_neg_score = sum(weight for word, weight in somewhat_negative.items() if word in text)
    neutral_score = sum(weight for word, weight in neutral.items() if word in text)
    somewhat_pos_score = sum(weight for word, weight in somewhat_positive.items() if word in text)
    very_pos_score = sum(weight for word, weight in very_positive.items() if word in text)
    
    # Calculate total sentiment score
    total_negative = very_neg_score * 2 + somewhat_neg_score
    total_positive = very_pos_score * 2 + somewhat_pos_score
    total_neutral = neutral_score
    
    # Analyze context patterns
    context_score = 0
    
    # Check for question patterns (slightly positive/neutral)
    if "?" in text:
        context_score += 0.5
    
    # Check for exclamation patterns (intensifies sentiment)
    exclamation_count = text.count("!")
    if exclamation_count > 0:
        if total_negative > total_positive:
            context_score -= min(exclamation_count, 3) * 0.5
        elif total_positive > total_negative:
            context_score += min(exclamation_count, 3) * 0.5
    
    # Check for complaint escalation patterns
    if "speak to manager" in text or "supervisor" in text or "escalate" in text:
        context_score -= 1.5
    
    # Check for urgency patterns
    if "immediately" in text or "urgent" in text or "as soon as possible" in text or "emergency" in text:
        context_score -= 1
    
    # Check for satisfaction patterns
    if "resolved" in text or "fixed" in text or "solved" in text:
        context_score += 1
    
    # Check for dissatisfaction patterns
    if "still not working" in text or "still broken" in text or "again" in text:
        context_score -= 1.5
    
    # Determine base sentiment score (1-10)
    if total_negative > total_positive + total_neutral:
        # Negative sentiment dominates
        if very_neg_score > somewhat_neg_score:
            base_score = 2  # Very negative
        else:
            base_score = 4  # Somewhat negative
    elif total_positive > total_negative + total_neutral:
        # Positive sentiment dominates
        if very_pos_score > somewhat_pos_score:
            base_score = 9  # Very positive
        else:
            base_score = 7  # Somewhat positive
    else:
        # Mixed or neutral sentiment - avoid defaulting to exactly 5
        if total_neutral > (total_positive + total_negative):
            base_score = 6  # Slightly positive neutral
        else:
            # Randomize slightly to avoid always returning 5
            import random
            base_score = random.choice([4, 6])
    
    # Apply context adjustments
    final_score = base_score + context_score
    
    # Additional context adjustments
    if "but" in text and base_score > 5:
        final_score -= 1  # "but" often negates positive sentiment
    if "however" in text and base_score > 5:
        final_score -= 1
    if "despite" in text and base_score < 6:
        final_score += 1  # "despite" often indicates some positive aspect
    if "thank" in text and "not" not in text:
        final_score += 1  # Gratitude is positive
    if "please" in text and base_score < 4:
        final_score += 0.5  # Politeness softens negative sentiment
    
    # Ensure score is within 1-10 range and avoid exactly 5
    sentiment_score = max(1, min(10, round(final_score)))
    if sentiment_score == 5:
        # Push away from neutral 5 based on the dominant sentiment direction
        if total_negative > total_positive:
            sentiment_score = 4
        else:
            sentiment_score = 6
    
    # Determine sentiment category
    if sentiment_score <= 3:
        sentiment_category = "Very negative"
        key_emotions = ["frustration", "disappointment", "anger"]
    elif sentiment_score <= 5:
        sentiment_category = "Somewhat negative"
        key_emotions = ["concern", "mild frustration", "dissatisfaction"]
    elif sentiment_score <= 7:
        sentiment_category = "Neutral to slightly positive"
        key_emotions = ["calm", "neutral", "mild satisfaction"]
    else:
        sentiment_category = "Very positive"
        key_emotions = ["satisfaction", "appreciation", "happiness"]
    
    # Determine urgency based on keywords and sentiment
    urgent_keywords = ["immediately", "urgent", "emergency", "safety", "dangerous", 
                       "critical", "asap", "right away", "serious"]
    urgent = any(word in text for word in urgent_keywords) or sentiment_score <= 2
    
    # Select only 2-3 most relevant emotions based on the text
    if "angry" in text or "furious" in text:
        key_emotions = ["anger"] + key_emotions[:1]
    elif "disappointed" in text:
        key_emotions = ["disappointment"] + key_emotions[:1]
    elif "worried" in text or "concerned" in text:
        key_emotions = ["concern"] + key_emotions[:1]
    elif "happy" in text or "pleased" in text:
        key_emotions = ["happiness"] + key_emotions[:1]
    elif "grateful" in text or "thank" in text:
        key_emotions = ["gratitude"] + key_emotions[:1]
    
    # Generate explanation
    if sentiment_score <= 3:
        explanation = f"The text contains strong negative language and expresses significant dissatisfaction."
    elif sentiment_score <= 5:
        explanation = f"The text expresses some concerns or mild frustration, but without extreme negative emotion."
    elif sentiment_score <= 7:
        explanation = f"The text is generally neutral with some positive elements, indicating basic satisfaction."
    else:
        explanation = f"The text contains strong positive language, indicating high satisfaction or appreciation."
    
    return {
        "sentiment_score": sentiment_score,
        "sentiment_category": sentiment_category,
        "key_emotions": key_emotions[:2],  # Limit to 2 emotions
        "urgent": urgent,
        "explanation": explanation
    }

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze sentiment of text')
    parser.add_argument('--text', type=str, required=True, help='Text to analyze')
    parser.add_argument('--model_name', type=str, default="cohere_oci", help='Model to use for analysis')
    
    args = parser.parse_args()
    
    # Analyze sentiment
    result = analyze_sentiment(args.text, args.model_name)
    
    # Print result as JSON
    print(json.dumps(result))