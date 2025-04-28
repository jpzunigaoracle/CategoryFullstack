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
    categories: List = []
    reports: List = []


class FeedbackAgent:
    def __init__(self, model_name: str = "cohere_oci", categ_with_embedding=False):
        self.model_name = model_name
        self.model = self.initialize_model()
        self.memory = MemorySaver()
        self.builder = self.setup_graph()
        self.messages = handler.read_messages(
            filepath="backend/data/ComplainsList.csv"  # Changed from complaints_messages.csv to ComplainsList.csv
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
        state.messages_info = [json.loads(response.content)]
        return {"messages_info": state.messages_info}

    def categorization_node(self, state: AgentState):
        if self.categ_with_embedding:
            pass
        else:
            response = self.model.invoke(
                [
                    SystemMessage(
                        content=llm_config.get_prompt(
                            self.model_name, "CATEGORIZATION_SYSTEM"
                        )
                    ),
                    HumanMessage(
                        content=llm_config.get_prompt(
                            self.model_name, "CATEGORIZATION_USER"
                        ).format(MESSAGE_BATCH=state.messages_info)
                    ),
                ]
            )
            content = [json.loads(response.content)]
            state.categories = handler.match_categories(state.messages_info, content)
            print(state.categories)
        return {"categories": state.categories}

    def generate_report_node(self, state: AgentState):
        response = self.model.invoke(
            [
                SystemMessage(
                    content=llm_config.get_prompt(self.model_name, "REPORT_GEN")
                ),
                HumanMessage(content=f"Message info: {state.categories}"),
            ]
        )
        state.reports = response.content
        return {"reports": [response.content]}
        

    def setup_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("summarize", self.summarization_node)
        builder.add_node("categorize", self.categorization_node)
        builder.add_node("generate_report", self.generate_report_node)

        builder.set_entry_point("summarize")
        builder.add_edge("summarize", "categorize")
        builder.add_edge("categorize", "generate_report")

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
            "categories": [],
            "reports":  [],
        }

        # Step-by-step execution
        for state in self.builder.stream(initial_state, thread):
            yield state  # Yield each intermediate step to allow step-by-step execution


# Constants

query_schema = {
    "title": "Queries",
    "description": "A list of search queries to gather information for research",
    "type": "object",
    "properties": {"queries": {"type": "array", "items": {"type": "string"}}},
    "required": ["queries"],
}

summarization_schema = {
    "title": "Summary",
    "description": "Message info",
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "sentiment_score": {"type": "string"},
        "summary": {"type": "string"},
    },
    "required": ["topic", "sentiment_score", "summary"],
}

categories_schema = {
    "title": "Categories",
    "description": "Hierarchical categorization of message summaries",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Unique identifier for the message",
            },
            "primary_category": {
                "type": "string",
                "description": "Broadest level category",
            },
            "secondary_category": {
                "type": "string",
                "description": "More specific domain within the primary category",
            },
            "tertiary_category": {
                "type": "string",
                "description": "Most specific classification within the secondary category",
            },
        },
        "required": [
            "id",
            "primary_category",
            "secondary_category",
            "tertiary_category",
        ],
    },
}

batch_categ_schema = {
    "title": "Queries",
    "description": "A list of search queries to gather information for research",
    "type": "object",
    "properties": {
        "queries": {
            "type": "array",
            "items": {
                "type": {
                    "title": "Categories",
                    "description": "Hierarchical categorization of message summaries",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Unique identifier for the message",
                            },
                            "primary_category": {
                                "type": "string",
                                "description": "Broadest level category",
                            },
                            "secondary_category": {
                                "type": "string",
                                "description": "More specific domain within the primary category",
                            },
                            "tertiary_category": {
                                "type": "string",
                                "description": "Most specific classification within the secondary category",
                            },
                        },
                        "required": [
                            "id",
                            "primary_category",
                            "secondary_category",
                            "tertiary_category",
                        ],
                    },
                }
            },
        }
    },
    "required": ["queries"],
}
