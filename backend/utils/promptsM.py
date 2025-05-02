# MESSAGE SUMMARIZATION
SUMMARIZATION = """\
You are an expert complaint analyzer. Your task is to:

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
\
"""

CATEGORIZATION_SYSTEM = """\
You are an expert content analyzer that categorizes user messages into a hierarchical taxonomy. You process batches of message summaries, each with a unique ID, and classify them into a 2-level nested category structure.

IMPORTANT CONSTRAINTS:
- Use EXACTLY 6 primary categories (these should match the categories created in the summarization step)
- Use 2-3 secondary categories per primary category to provide more detail
- Maintain consistent naming and logical hierarchical relationships

Analyze the following batch of message summaries and categorize each one into this constrained 2-level hierarchical taxonomy:

1. Primary category: Must be one of the 6 main categories identified earlier
2. Secondary category: More specific domain within the primary category

Return your analysis as a JSON array with each element containing "id", "primary_category", and "secondary_category".

**Example of expected categorization structure:**
- Primary: "Product Quality"
  - Secondary: "Manufacturing Defects"
  - Secondary: "Material Issues"
\
"""

CATEGORIZATION_USER = """\

Message Batch:
{MESSAGE_BATCH}
\
"""

REPORT_GEN = """\
# **Generate a Categorized JSON Report of Messages**

## **Task**  
You are an expert data analyst. Your task is to generate a structured and insightful JSON report analyzing a batch of messages based on their category levels, summaries, and sentiment scores. Each message is classified into three hierarchical category levels (Category Level 2 and Category Level 3).  

## **Instructions**  
Follow these steps to generate the report:  
1. **Group messages by Category Level 2**, then further organize them into Category Level 3 subcategories.  
2. **Summarize each category level** by aggregating key themes and trends from message summaries.  
3. **Analyze sentiment scores** by calculating the average, highest, and lowest sentiment scores for each category level (1=extremely negative, 10=extremely positive). 
4. **Identify key insights** such as common concerns, prevailing sentiment trends, and outliers.  
5. **Format the output as a structured JSON object** with the following structure:  

## **Output Format (JSON)**  
{
  "categories": [
    {
      "category_level_1": "Category Name",
      "summary": "Concise summary of messages in this category",
      "average_sentiment_score": 7.2,
      "highest_sentiment_message": {
        "summary": "Message summary",
        "sentiment_score": 10
      },
      "lowest_sentiment_message": {
        "summary": "Message summary",
        "sentiment_score": 2
      },
      "key_insights": [
        "Notable pattern 1",
        "Notable pattern 2"
      ],
      "subcategories": [
        {
          "category_level_2": "Subcategory Name",
          "summary": "Common themes from messages",
          "average_sentiment_score": 6.5,
          "sentiment_range": {
            "lowest": 3,
            "highest": 9
          },
          "notable_sentiment_trends": [
            "Trend 1",
            "Trend 2"
          ],
        }
      ]
    }
  ]
}
\
"""



# (LLAMA format) COMPETITOR REPORT PROMPTS
SUMMARIZATION_LLAMA = """<system>
You are an AI assistant that analyzes text and provides structured analysis. Your task is to examine the user's message, identify the main topic, create a concise summary, and evaluate the sentiment on a scale from 1 (negative) to 10 (positive). You must return your analysis in valid JSON format.
</system>

<user>
Analyze the following message and provide your analysis in valid JSON format with these fields: "main_topic", "summary", and "sentiment_score" (where 1 is extremely negative and 10 is extremely positive).

Message: {USER_MESSAGE}
</user>

<assistant>
I'll analyze this message carefully.

{
  "main_topic": "The primary subject matter of the message",
  "summary": "A concise 1-2 sentence summary of the key points",
  "sentiment_score": X
}

Let me verify:
- The main topic accurately represents the central theme
- The summary captures the essential information in 1-2 sentences
- The sentiment score correctly reflects the emotional tone on a 1-10 scale
- The output is valid, parseable JSON
</assistant>
"""

CATEGORIZATION_LLAMA = """<system>
You are an expert content analyzer that categorizes user messages into a hierarchical taxonomy. You process batches of message summaries, each with a unique ID, and classify them into a 3-level nested category structure. Your categorization must follow a consistent taxonomy with increasing specificity at each level.
</system>

<user>
Analyze the following batch of message summaries and categorize each one into a 3-level hierarchical taxonomy:

1. Primary category: Broadest level (e.g., "Human Resources", "Finance", "IT")
2. Secondary category: More specific domain within the primary category (e.g., "Policies", "Benefits", "Recruitment")
3. Tertiary category: Most specific classification (e.g., "Leaves", "Health Insurance", "Interview Process")

Ensure that each level builds upon the previous level with increasing specificity and follows logical parent-child relationships.

Return your analysis as a JSON array with each element containing "id", "primary_category", "secondary_category", and "tertiary_category".

Example of expected categorization structure:
- Primary: "Human Resources"
  - Secondary: "Policies"
    - Tertiary: "Leaves"
  - Secondary: "Benefits"
    - Tertiary: "Health Insurance"

Message Batch:
{MESSAGE_BATCH}
</user>

<assistant>
I've analyzed each message summary and categorized them according to the 3-level hierarchical taxonomy:

```json
[
  {
    "id": "msg_001",
    "primary_category": "Primary level category",
    "secondary_category": "Secondary level category within primary",
    "tertiary_category": "Tertiary level category within secondary"
  },
  {
    "id": "msg_002",
    "primary_category": "Primary level category",
    "secondary_category": "Secondary level category within primary",
    "tertiary_category": "Tertiary level category within secondary"
  },
  {
    "id": "msg_003",
    "primary_category": "Primary level category",
    "secondary_category": "Secondary level category within primary",
    "tertiary_category": "Tertiary level category within secondary"
  }
]

"""

REPORT_GEN_LLAMA = """<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>



You are an expert data analyst. Your task is to generate a structured and insightful JSON report analyzing a batch of messages based on their category levels, summaries, and sentiment scores. Each message is classified into three hierarchical category levels (Category Level 1, Category Level 2, and Category Level 3).

Follow these steps to generate the report:
1. **Group messages by Category Level 1**, then further organize them into Category Level 2 and Category Level 3 subcategories.
2. **Summarize each category level** by aggregating key themes and trends from message summaries.
3. **Analyze sentiment scores** by calculating the average, highest, and lowest sentiment scores for each category level.
4. **Identify key insights** such as common concerns, prevailing sentiment trends, and outliers.
5. **Format the output as a structured JSON object** with the following structure:

```json
{
  "categories": [
    {
      "category_level_1": "Category Name",
      "summary": "Concise summary of messages in this category",
      "average_sentiment_score": 7.2,
      "highest_sentiment_message": {
        "summary": "Message summary",
        "sentiment_score": 10
      },
      "lowest_sentiment_message": {
        "summary": "Message summary",
        "sentiment_score": 2
      },
      "key_insights": [
        "Notable pattern 1",
        "Notable pattern 2"
      ],
      "subcategories": [
        {
          "category_level_2": "Subcategory Name",
          "summary": "Common themes from messages",
          "average_sentiment_score": 6.5,
          "sentiment_range": {
            "lowest": 3,
            "highest": 9
          },
          "notable_sentiment_trends": [
            "Trend 1",
            "Trend 2"
          ],
          "subcategories": [
            {
              "category_level_3": "Sub-subcategory Name",
              "summary": "Detailed message patterns",
              "average_sentiment_score": 5.8,
              "sentiment_range": {
                "lowest": 1,
                "highest": 8
              },
              "notable_sentiment_trends": [
                "Specific insight based on sentiment analysis"
              ]
            }
          ]
        }
      ]
    }
  ]
}
"""
