# Prompts for sentiment analysis

# Main summarization prompt
SUMMARIZATION = """You are an expert complaint analyzer. Your task is to:

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
  {
    "id": "2",
    "summary": "Customer's dishwasher hasn't been delivered yet and they want status update.",
    "sentiment_score": 4,
    "date_created": "2023-02-05",
    "time_created": "2:15 PM",
    "date_ended": "2023-02-05",
    "time_ended": "2:30 PM"
  },
  ... and so on for each complaint
]

IMPORTANT: 
- Include EVERY complaint from the input
- Make sure each summary is concise but informative
- Ensure sentiment scores accurately reflect customer satisfaction
- Include date_created, time_created, date_ended, and time_ended fields for each complaint
- Return valid JSON that can be parsed
"""

# Define the prompt sets for different models
PROMPT_SETS = {
    "cohere_oci": {
        "summarization": SUMMARIZATION
    },
    "meta_oci": {
        "summarization": SUMMARIZATION
    }
}
