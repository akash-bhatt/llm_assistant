import streamlit as st
import random
import time
import os
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

st.title("LLM Assistant")
os.environ["LANGSMITH_TRACING"] = st.secrets["LANGSMITH_TRACING"]
os.environ["LANGSMITH_ENDPOINT"] = st.secrets["LANGSMITH_ENDPOINT"]
os.environ["LANGSMITH_PROJECT"] = st.secrets["LANGSMITH_PROJECT"]
os.environ["LANGSMITH_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]

# Initialize the Bedrock client

# check if bedrock client is already initialized in session state

if "bedrock_model" not in st.session_state:
    st.session_state.bedrock_model = init_chat_model("us.meta.llama4-scout-17b-instruct-v1:0", model_provider="bedrock_converse")
   
# Use the existing Bedrock client if available, otherwise create a new one
bedrock_model = st.session_state.bedrock_model

def get_langchain_prompt_template():
    return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Answer all questions to the best of your ability. Unless specifically told to use a different language, always respond in {language}. If you do not know something, gracefully respond that you do not know.",
                ),
                MessagesPlaceholder(variable_name="messages_lgraph"),
            ]
        )

def get_st_prompt_template():
    """Get the prompt template from session state or create a new one."""
    if "prompt_template" in st.session_state:
        return st.session_state.prompt_template
    else:
        prompt_template = get_langchain_prompt_template()
        st.session_state.prompt_template = prompt_template
        return prompt_template


class State(TypedDict):
    messages_lgraph: Annotated[Sequence[BaseMessage], add_messages]
    language: str

# Define a new graph
def get_langgraph():
    """Get the workflow from session state or create a new one."""
    if "workflow" in st.session_state:
        return st.session_state.inv
    else:
        workflow = StateGraph(state_schema=State)
        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)  
        # Add memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

# generate a streamlit function to save workflow in session state
def get_st_workflow():
    """Get the workflow from session state or create a new one."""
    if "workflow" in st.session_state:
        return st.session_state.workflow
    else:
        workflow = get_langgraph()
        st.session_state.workflow = workflow
        return workflow

# Define the function that calls the models
def call_model(state: State):
    prompt = get_st_prompt_template().invoke(state)
    #print(f"Prompt: {prompt}")
    response = bedrock_model.invoke(prompt)
    return {"messages_lgraph": response}


# generate a random thread_id for the chat
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(random.randint(100000, 999999))

config = {"configurable": {"thread_id": st.session_state.thread_id}}
language = "English"  # Set the language for the system prompt

# Initialize chat history
if "messages_stlit" not in st.session_state:
    aicontent = "Let's start chatting! Ask me anything."
    st.session_state.messages_stlit = [{"role": "assistant", "content": aicontent}]
    input_messages = [AIMessage(aicontent)]

# Display chat messages from history on app rerun
for message_stlit in st.session_state.messages_stlit:
    with st.chat_message(message_stlit["role"]):
        st.markdown(message_stlit["content"])

# Accept user input
if prompt := st.chat_input():
    # Add user message to chat history
    st.session_state.messages_stlit.append({"role": "user", "content": prompt})
    input_messages = [HumanMessage(prompt)]
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)


    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        full_response = ""
        try:
            for chunk, metadata in get_st_workflow().stream(
                {"messages_lgraph": input_messages, "language": language},
                config,
                stream_mode="messages",
            ):
                #print(chunk.content)
                if isinstance(chunk, AIMessage):  # Filter to just model responses
                    if len(chunk.content) > 0:
                        if 'text' in chunk.content[0]:
                            full_response += chunk.content[0]['text']
                            time.sleep(0.05)
                            message_placeholder.markdown(full_response + "▌")
                
        except Exception as e:
            st.error(f"ERROR: Can't invoke '{st.secrets['bedrock_model_id']}'. Reason: {e}")
            full_response = "Sorry, I encountered an error processing your request." 
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages_stlit.append({"role": "assistant", "content": full_response})
