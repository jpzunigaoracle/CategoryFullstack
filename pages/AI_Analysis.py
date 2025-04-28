import streamlit as st
import pandas as pd
from backend.utils import llm_configM as llm_config
from backend.utils.promptsM import SUMMARIZATION
import plotly.express as px
from backend.feedback_wrapperM import FeedbackAgentWrapperM  # This import will now work correctly

st.set_page_config(page_title="AI Analysis", layout="wide")

def load_complaints():
    df = pd.read_csv("backend/data/ComplainsList.csv")
    return df

def process_complaints(complaints_df):
    # Initialize the FeedbackAgentM wrapper
    agent = FeedbackAgentWrapperM()  # Changed to M version
    
    # Process the complaints step by step
    step_outputs = {}
    current_step = None
    
    while current_step != "FINALIZED":
        next_step, output = agent.run_step_by_step()
        if output:
            step_outputs[next_step] = output
        current_step = next_step
    
    # Extract the processed results
    if 'messages_info' in step_outputs:
        results = step_outputs['messages_info'][0]
        
        # Update the DataFrame with AI analysis results
        complaints_df['assigned_category'] = [item.get('assigned_category', '') for item in results]
        complaints_df['summary'] = [item.get('summary', '') for item in results]
        complaints_df['sentiment_score'] = [item.get('sentiment_score', 0) for item in results]
    
    return complaints_df

def display_complaints_with_categories(data):
    st.subheader("📋 Customer Complaints with AI Classifications")
    
    # Add debug information
    print("Data columns:", data.columns.tolist())
    print("Data shape:", data.shape)
    
    # Create a DataFrame with complaints and their classifications
    df_display = pd.DataFrame({
        'Customer Complaint Dialog': data['CustomerComplaintDialog'],  # Fixed column name
        'AI Category': data['assigned_category'] if 'assigned_category' in data else '',
        'Summary': data['summary'] if 'summary' in data else '',
        'Sentiment Score': data['sentiment_score'] if 'sentiment_score' in data else '',
        'Date & Time Created': data['Date&TimeCreated'],  # Fixed column name
        'Date & Time Ended': data['Date&TimeEnded']  # Fixed column name
    })
    
    # Display the DataFrame
    st.dataframe(df_display)
    
    # Display category statistics if categories exist
    if 'AI Category' in df_display.columns and df_display['AI Category'].any():
        st.subheader("📊 Category Distribution")
        category_counts = df_display['AI Category'].value_counts()
        fig = px.pie(values=category_counts.values, names=category_counts.index, 
                     title="Distribution of Complaints Across Categories")
        st.plotly_chart(fig)

def main():
    st.title("🤖 AI Complaint Analysis Dashboard")
    
    # Load complaints
    complaints_df = load_complaints()
    
    if st.button("Start AI Analysis"):
        with st.spinner("Analyzing complaints..."):
            # Process complaints through AI analysis
            processed_df = process_complaints(complaints_df)
            st.success("Analysis complete!")
            
            # Display results
            display_complaints_with_categories(processed_df)

if __name__ == "__main__":
    main()
