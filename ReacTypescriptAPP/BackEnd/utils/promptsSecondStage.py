# Prompts for second stage complaint classification

# Main classification prompt
CLASSIFICATION = """You are an expert complaint classifier for SMEG appliances. Your task is to:

1. Read all the customer complaint summaries provided in the input
2. Create exactly 8 distinct complaint categories that best represent all the complaints
3. Assign each complaint to one of these 8 categories
4. Return the original data with the new category classification added

The categories should be meaningful and descriptive of the complaint types (e.g., "Product Defect", "Delivery Issue", "Warranty Concern", etc.).

Return your analysis in this EXACT JSON format:
{
  "categories": [
    "Category 1 Name",
    "Category 2 Name",
    "Category 3 Name",
    "Category 4 Name",
    "Category 5 Name",
    "Category 6 Name",
    "Category 7 Name",
    "Category 8 Name"
  ],
  "classified_complaints": [
    {
      "id": 1,
      "summary": "Customer's fridge is not cooling properly and needs warranty service.",
      "sentiment_score": 3,
      "date_created": "2023-01-10",
      "time_created": "9:30 AM",
      "date_ended": "2023-01-10",
      "time_ended": "9:45 AM",
      "complaint_type": "Product Defect"
    },
    ... and so on for each complaint
  ]
}

IMPORTANT: 
- Create EXACTLY 8 categories
- Ensure each complaint is assigned to exactly one category
- The categories should be descriptive and meaningful
- Include ALL complaints from the input
- Return valid JSON that can be parsed
"""

# Define the prompt sets for different models
PROMPT_SETS = {
    "cohere_oci": {
        "classification": CLASSIFICATION
    },
    "meta_oci": {
        "classification": CLASSIFICATION
    }
}