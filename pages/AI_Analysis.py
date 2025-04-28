import streamlit as st
import pandas as pd
import json
from backend.utils import llm_configM
from backend.utils.promptsM import SUMMARIZATION
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_core.messages import HumanMessage, SystemMessage
import plotly.express as px

# ---------------------------
# 🔧 Page Setup
# ---------------------------
st.set_page_config(page_title="AI Complaint Analysis", layout="wide")
st.title("📬 Complaint Synthesis Dashboard")
st.caption("Summarization | Categorization (Max 6 Classes) | Sentiment | Timestamps")

# ---------------------------
# 📊 Visual Flowchart
# ---------------------------
def create_flowchart(active="summarize"):
    steps = ["load", "summarize", "done"]
    edges = [("load", "summarize"), ("summarize", "done")]
    dot = "digraph G {\n"
    dot += '    graph [fontname="Courier New"];\n'

    for step in steps:
        color = "gold" if step == active else "paleturquoise"
        dot += f'    "{step}" [shape=box, style="rounded,filled", fillcolor={color}];\n'

    for s, t in edges:
        dot += f'    "{s}" -> "{t}" [color=dimgrey, penwidth=1.5];\n'
    dot += "}"
    return dot

# ---------------------------
# 📂 Load Complaints CSV
# ---------------------------
@st.cache_data
def load_complaints():
    df = pd.read_csv("backend/data/Complains List.csv")
    return df

df = load_complaints()

# Show initial preview
st.subheader("📄 Raw Input Data")
st.dataframe(df[["Customer Complaint Dialog", "Date & Time Created", "Date & Time Ended"]], use_container_width=True)

# ---------------------------
# 🤖 Load LLM from config
# ---------------------------
model_cfg = llm_configM.MODEL_REGISTRY["cohere_oci"]
model = ChatOCIGenAI(
    model_id=model_cfg["model_id"],
    service_endpoint=model_cfg["service_endpoint"],
    compartment_id=model_cfg["compartment_id"],
    provider=model_cfg["provider"],
    auth_type=model_cfg["auth_type"],
    auth_profile=model_cfg["auth_profile"],
    model_kwargs=model_cfg["model_kwargs"],
)

# ---------------------------
# 🔍 Run LLM Summarization
# ---------------------------
def summarize_all_messages(df):
    messages = []
    for i, row in df.iterrows():
        messages.append({
            "id": f"msg_{i+1:03}",
            "Date & Time Created": row["Date & Time Created"],
            "Date & Time Ended": row["Date & Time Ended"],
            "message": row["Customer Complaint Dialog"]
        })

    user_prompt = f"Analyze the following csv file of user complain messages:\n{json.dumps(messages, indent=2)}"

    response = model.invoke([
        SystemMessage(content=SUMMARIZATION),
        HumanMessage(content=user_prompt)
    ])

    try:
        output_json = json.loads(response.content)
        return output_json
    except Exception as e:
        st.error("⚠️ Failed to parse model output. Check format.")
        st.code(response.content)
        return None

# ---------------------------
# 🚀 Main Logic
# ---------------------------
if "flow_completed" not in st.session_state:
    st.session_state.flow_completed = True

if st.sidebar.button("Start AI Analysis", disabled=not st.session_state.flow_completed):
    col1, _ = st.columns([0.4, 0.6])
    st.session_state.flow_completed = False

    with col1:
        st.subheader("📍 Analysis Flow")
        st.graphviz_chart(create_flowchart("summarize"))

    st.divider()
    st.info("⏳ Summarizing complaints and categorizing into 6 types...")

    with st.spinner("Running LLM summarization..."):
        result = summarize_all_messages(df)

    if result:
        output_df = pd.DataFrame(result)
        output_df["sentiment_score"] = output_df["sentiment_score"].astype(int)

        st.success("✅ Summarization complete!")
        st.subheader("📊 Synthesized Complaints Table")
        st.dataframe(output_df, use_container_width=True)

        # Count unique categories
        category_counts = output_df["complain category"].value_counts()
        st.markdown("### 📂 Complaint Category Distribution (Max 6)")
        st.write(f"**Found {len(category_counts)} unique categories**")

        fig = px.bar(
            category_counts.reset_index(),
            x="index",
            y="complain category",
            labels={"index": "Category", "complain category": "Count"},
            title="Complaint Frequency by Category",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Download option
        csv = output_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, file_name="complaint_synthesis.csv", mime="text/csv")

    else:
        st.error("⚠️ No results returned.")
