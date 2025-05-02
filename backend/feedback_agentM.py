import json
import logging
from typing import List

from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

import backend.utils.llm_configM as llm_config
import backend.message_handlerM as handler

# Set up logging
logging.getLogger("oci").setLevel(logging.DEBUG)


class AgentState(BaseModel):
    messages_info: List = []
    reports: List = []


class FeedbackAgent:
    def __init__(self, model_name: str = "cohere_oci", categ_with_embedding=False):
        self.model_name = model_name
        self.model = self.initialize_model()
        self.memory = MemorySaver()
        self.builder = self.setup_graph()
        self.messages = handler.read_messages(
            filepath="backend/data/ComplainsList.json"
        )
        self.categ_with_embedding = categ_with_embedding

    def initialize_model(self):
        if self.model_name not in llm_config.MODEL_REGISTRY:
            raise ValueError(f"Unknown model: {self.model_name}")

        model_config = llm_config.MODEL_REGISTRY[self.model_name]

        return ChatOCIGenAI(
            model_id=model_config["model_id"],
            service_endpoint=model_config["service_endpoint"],
            compartment_id=model_config["compartment_id"],
            provider=model_config["provider"],
            auth_type=model_config["auth_type"],
            auth_profile=model_config["auth_profile"],
            model_kwargs=model_config["model_kwargs"],
        )
    
    def initialize_embeddings(self):
        if self.model_name not in llm_config.MODEL_REGISTRY:
            raise ValueError(f"Unknown model: {self.model_name}")

        model_config = llm_config.MODEL_REGISTRY[self.model_name]

        embeddings = OCIGenAIEmbeddings(
            model_id=model_config["embedding_model"],
            service_endpoint=model_config["service_endpoint"],
            truncate="NONE",
            compartment_id=model_config["compartment_id"],
            auth_type=model_config["auth_type"],
            auth_profile=model_config["auth_profile"],
            )
        return embeddings


    def summarization_node(self, state: AgentState):
        response = self.model.invoke(
            [
                SystemMessage(
                    content=llm_config.get_prompt(self.model_name, "SUMMARIZATION")
                ),
                HumanMessage(content=f"Message batch: {self.messages}"),
            ]
        )
        try:
            state.messages_info = [json.loads(response.content)]
            print(f"Parsed messages_info: {state.messages_info}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response.content}")
            state.messages_info = [{"error": "Failed to parse LLM response"}]
        return {"messages_info": state.messages_info}

    def generate_report_node(self, state: AgentState):
        # Simply pass through the summarization results
        state.reports = state.messages_info
        return {"reports": state.messages_info}

    def setup_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("summarize", self.summarization_node)
        builder.add_node("generate_report", self.generate_report_node)

        builder.set_entry_point("summarize")
        builder.add_edge("summarize", "generate_report")
        builder.add_edge("generate_report", END)
        
        return builder.compile(checkpointer=self.memory)

    def get_graph(self):
        return self.builder.get_graph()

    def run(self):
        thread = {"configurable": {"thread_id": "1"}}
        for s in self.builder.stream(
            config=thread,
        ):
            print(f"\n \n{s}")

    def run_step_by_step(self):
        """
        Run the graph step by step, yielding each state in the process.
        """
        thread = {"configurable": {"thread_id": "1"}}
        # Step-by-step execution
        initial_state = {
            "messages_info": [],
            "reports":  [],
        }

        # Step-by-step execution
        for state in self.builder.stream(initial_state, thread):
            yield state  # Yield each intermediate step to allow step-by-step execution


# Constants

summarization_schema = {
    "title": "Summary",
    "description": "Message info",
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "sentiment_score": {"type": "string"},
    },
    "required": ["summary", "sentiment_score"],
}
