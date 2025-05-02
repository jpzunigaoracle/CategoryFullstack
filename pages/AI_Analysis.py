import streamlit as st
import pandas as pd
import json
import os
from backend.utils import llm_configM as llm_config
from backend.utils.promptsM import SUMMARIZATION
import plotly.express as px
from backend.feedback_wrapperM import FeedbackAgentWrapperM

st.set_page_config(page_title="AI Analysis", layout="wide")

def load_complaints():
    """Load complaints from JSON file and convert to DataFrame"""
    try:
        with open("backend/data/ComplainsList.json", encoding='utf-8') as file:
            data = json.load(file)
        
        # Convert JSON to DataFrame
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error loading complaints: {e}")
        return pd.DataFrame()

def process_complaints(complaints_df):
    # Initialize the FeedbackAgentM wrapper
    agent = FeedbackAgentWrapperM()
    
    # Process the complaints step by step
    step_outputs = {}
    current_step = None
    
    print("Starting complaint processing...")
    
    while current_step != "FINALIZED":
        next_step, output = agent.run_step_by_step()
        print(f"Processing step: {next_step}")
        if output:
            step_outputs[next_step] = output
            # Add debug print
            print(f"Step: {next_step}, Output keys: {list(output.keys())}")
        else:
            print(f"No output for step: {next_step}")
        current_step = next_step
    
    print(f"Final step_outputs: {step_outputs.keys()}")
    
    # Save results to output.json file
    save_results_to_json(step_outputs)
    
    # Return the raw step_outputs for display
    return step_outputs

def save_results_to_json(step_outputs):
    """Save analysis results to output.json file"""
    results = None
    
    # Check for results in generate_report step first (this contains the final results)
    if 'generate_report' in step_outputs and 'reports' in step_outputs['generate_report']:
        results = step_outputs['generate_report']['reports']
    # Then check for results in summarize step as fallback
    elif 'summarize' in step_outputs and 'messages_info' in step_outputs['summarize']:
        results = step_outputs['summarize']['messages_info']
    
    if results:
        # Create data directory if it doesn't exist
        os.makedirs("backend/data", exist_ok=True)
        
        # Print debug info
        print(f"Saving results to output.json: {type(results)} with length {len(results) if isinstance(results, list) else 'not a list'}")
        
        # Save results to output.json - ensure we're saving the actual data
        try:
            # If results is a list containing one item that's the actual data, extract it
            if isinstance(results, list) and len(results) == 1:
                data_to_save = results[0]
            else:
                data_to_save = results
                
            with open("backend/data/output.json", "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=2)
            print("Results successfully saved to backend/data/output.json")
        except Exception as e:
            print(f"Error saving results: {e}")
    else:
        print("No results found to save")
        print(f"Available keys in step_outputs: {step_outputs.keys()}")
        
        # Try to extract raw data from step_outputs for debugging
        for key in step_outputs:
            print(f"Content of {key}: {step_outputs[key]}")
            # Try to dig deeper into the structure
            if isinstance(step_outputs[key], dict):
                for subkey, subvalue in step_outputs[key].items():
                    print(f"  - {subkey}: {type(subvalue)}")
                    if subkey == 'reports' or subkey == 'messages_info':
                        try:
                            with open("backend/data/output.json", "w", encoding="utf-8") as f:
                                json.dump(subvalue, f, indent=2)
                            print(f"Saved {subkey} to output.json")
                            return
                        except Exception as e:
                            print(f"Error saving {subkey}: {e}")
        
        # Create an empty but valid JSON array to prevent loading errors
        try:
            with open("backend/data/output.json", "w", encoding="utf-8") as f:
                json.dump([], f)
            print("Created empty but valid JSON array in output.json")
        except Exception as e:
            print(f"Error creating empty JSON file: {e}")

def display_json_results(step_outputs):
    """Display the JSON results from the analysis"""
    st.subheader("📋 AI Analysis Results")
    
    # First try to get results directly from step_outputs
    results = None
    report_text = None
    
    # Check if we have generate_report data in step_outputs
    if step_outputs and 'generate_report' in step_outputs:
        if 'reports' in step_outputs['generate_report']:
            report_data = step_outputs['generate_report']['reports']
            
            # If it's a list with one item, extract it
            if isinstance(report_data, list) and len(report_data) > 0:
                report_text = report_data[0]
            else:
                report_text = report_data
                
            # Try to parse as JSON if it's a string
            if isinstance(report_text, str):
                try:
                    results = json.loads(report_text)
                    print(f"Successfully parsed report text as JSON")
                except json.JSONDecodeError:
                    # If it's not valid JSON, just use it as text
                    print(f"Report text is not valid JSON, using as plain text")
    
    # If we couldn't get results from step_outputs, try loading from file
    if results is None and os.path.exists("backend/data/output.json"):
        try:
            with open("backend/data/output.json", "r", encoding="utf-8") as f:
                file_content = f.read().strip()
                if file_content:  # Check if file is not empty
                    results = json.loads(file_content)
                    print(f"Loaded results from file: {type(results)}")
                else:
                    st.warning("Output file exists but is empty. Please run the analysis again.")
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON from output file: {e}")
            # Fallback to step_outputs
            results = extract_results_from_step_outputs(step_outputs)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Table View", "Formatted View", "Raw JSON", "Report Text"])
    
    # Display results in different formats
    if results:
        with tab1:
            # Display results as a table
            if isinstance(results, list):
                # Convert list of dictionaries to DataFrame
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
            elif isinstance(results, dict) and "categories" in results:
                # Handle report format with categories
                categories_data = []
                for category in results["categories"]:
                    category_data = {
                        "category": category["category_level_1"],
                        "summary": category["summary"],
                        "avg_sentiment": category["average_sentiment_score"]
                    }
                    categories_data.append(category_data)
                df = pd.DataFrame(categories_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Results format not suitable for table view")
        
        with tab2:
            # Display each complaint analysis in a more readable format
            if isinstance(results, list):
                for item in results:
                    if isinstance(item, dict):
                        with st.expander(f"Complaint #{item.get('id', 'N/A')} - {item.get('summary', '')[:50]}..."):
                            cols = st.columns(2)
                            with cols[0]:
                                st.markdown("**Summary:**")
                                st.write(item.get('summary', 'No summary available'))
                                
                                st.markdown("**Sentiment Score:**")
                                sentiment = float(item.get('sentiment_score', 0))
                                st.progress(sentiment/10)
                                st.write(f"{sentiment}/10")
                            
                            with cols[1]:
                                st.markdown("**Date & Time Created:**")
                                st.write(f"{item.get('date_created', '')} {item.get('time_created', '')}")
                                
                                st.markdown("**Date & Time Ended:**")
                                st.write(f"{item.get('date_ended', '')} {item.get('time_ended', '')}")
            elif isinstance(results, dict) and "categories" in results:
                # Display categories in a more readable format
                for category in results["categories"]:
                    with st.expander(f"Category: {category['category_level_1']}"):
                        st.markdown(f"**Summary:** {category['summary']}")
                        st.markdown(f"**Average Sentiment:** {category['average_sentiment_score']}")
                        
                        # Display highest and lowest sentiment messages
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown("**Highest Sentiment Message:**")
                            st.write(category['highest_sentiment_message']['summary'])
                            st.write(f"Score: {category['highest_sentiment_message']['sentiment_score']}")
                        
                        with cols[1]:
                            st.markdown("**Lowest Sentiment Message:**")
                            st.write(category['lowest_sentiment_message']['summary'])
                            st.write(f"Score: {category['lowest_sentiment_message']['sentiment_score']}")
                        
                        # Display key insights
                        st.markdown("**Key Insights:**")
                        for insight in category.get('key_insights', []):
                            st.write(f"- {insight}")
                        
                        # Display subcategories if available
                        if 'subcategories' in category:
                            st.markdown("**Subcategories:**")
                            for subcategory in category['subcategories']:
                                with st.expander(f"Subcategory: {subcategory['category_level_2']}"):
                                    st.write(subcategory['summary'])
                                    st.write(f"Average Sentiment: {subcategory['average_sentiment_score']}")
            else:
                st.warning("Results format not suitable for formatted view")
        
        with tab3:
            # Display the raw JSON
            st.json(results)
            
            # Add download button
            json_str = json.dumps(results, indent=2)
            st.download_button(
                label="Download JSON Results",
                data=json_str,
                file_name="complaint_analysis.json",
                mime="application/json"
            )
    
    # Display the raw report text if available
    with tab4:
        if report_text:
            st.subheader("Raw Report Text")
            st.text_area("Report Content", report_text, height=400)
            
            # Add download button for text
            st.download_button(
                label="Download Report Text",
                data=report_text,
                file_name="complaint_report.txt",
                mime="text/plain"
            )
        else:
            st.warning("No report text available. Please run the analysis first.")

def extract_results_from_step_outputs(step_outputs):
    """Helper function to extract results from step_outputs"""
    if not step_outputs:
        return None
        
    # Try to extract from generate_report first
    if 'generate_report' in step_outputs and 'reports' in step_outputs['generate_report']:
        reports = step_outputs['generate_report']['reports']
        if isinstance(reports, list) and len(reports) > 0:
            return reports[0]
        return reports
    
    # Then try from summarize
    if 'summarize' in step_outputs and 'messages_info' in step_outputs['summarize']:
        messages_info = step_outputs['summarize']['messages_info']
        if isinstance(messages_info, list) and len(messages_info) > 0:
            return messages_info[0]
        return messages_info
    
    return None

def main():
    st.title("🤖 AI Complaint Analysis Dashboard")
    
    # Load complaints
    complaints_df = load_complaints()
    
    # Check if output.json exists and show a message
    if os.path.exists("backend/data/output.json"):
        st.info("Previous analysis results are available. You can run a new analysis or view the existing results.")
    
    if st.button("Start AI Analysis"):
        with st.spinner("Analyzing complaints..."):
            # Process complaints through AI analysis
            step_outputs = process_complaints(complaints_df)
            st.session_state['step_outputs'] = step_outputs
            st.success("Analysis complete!")
            
            # Display results
            display_json_results(step_outputs)
    else:
        # Check if we have previous results to display
        if os.path.exists("backend/data/output.json"):
            display_json_results({})
        elif 'step_outputs' in st.session_state:
            display_json_results(st.session_state['step_outputs'])

if __name__ == "__main__":
    main()
