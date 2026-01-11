import os
import logging

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Configure logging to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="AI SQL Agent", page_icon=":robot_face:")

st.title("AI SQL Agent")


def get_db_uri():
    return (
        f"postgresql+psycopg2://{st.session_state.db_user}:{st.session_state.db_password}"
        f"@{st.session_state.db_host}:{st.session_state.db_port}/{st.session_state.db_name}"
    )


def get_agent_executor(db_uri, model_name, api_key):
    try:
        logger.info(f"Connecting to database at {db_uri.split('@')[1]}")
        # Add connection arguments for timeout
        db = SQLDatabase.from_uri(
            db_uri,
            engine_args={
                "connect_args": {
                    "connect_timeout": 10
                }
            }
        )
        # Test connection
        db.run("SELECT 1")
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        st.error(f"Could not connect to database. Ensure Docker is running. Error: {e}")
        st.stop()

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
        request_timeout=60,
        streaming=False,
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    custom_prefix = (
        "You are an agent designed to interact with a {dialect} database.\n"
        "Given an input question, create a syntactically correct {dialect} query to run, "
        "then look at the results of the query and return the answer.\n"
        "If the SQL query returns no results, you MUST state that no data was found for that query, "
        "rather than saying you don't know the answer.\n"
        "You have access to the conversation history. Use it to resolve references like 'that one', 'him', 'her', etc.\n"
    )

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type="zero-shot-react-description",
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        prefix=custom_prefix,
    )
    agent_executor.max_execution_time = 120
    return agent_executor


def handle_chat(agent_executor, prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Create a container for the status and thoughts
        status_container = st.container()
        st_callback = StreamlitCallbackHandler(status_container, expand_new_thoughts=True)

        history_str = ""
        for msg in st.session_state.messages[:-1]:
            history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"
        full_input = f"Conversation History:\n{history_str}\nQuestion: {prompt}"

        try:
            logger.info("Invoking agent...")
            response_container = st.empty()
            response_container.info("Thinking...")
            
            response = agent_executor.invoke(
                {"input": full_input}, 
                {"callbacks": [st_callback]}
            )

            logger.info("Agent invocation complete")
            final_answer = response["output"]
            intermediate_steps = response.get("intermediate_steps", [])

            last_sql = ""
            for action, _ in intermediate_steps:
                if action.tool == "sql_db_query":
                    last_sql = action.tool_input

            full_content = ""
            if last_sql:
                full_content += f"**SQL Query:**\n```sql\n{last_sql}\n```\n\n"

            full_content += final_answer
            response_container.markdown(full_content)
            st.session_state.messages.append({"role": "assistant", "content": full_content})
            
        except Exception as e:
            logger.error(f"Error during agent execution: {e}")
            error_str = str(e)
            if "Could not parse LLM output:" in error_str:
                raw_output = error_str.split("Could not parse LLM output:")[1].strip()
                if (raw_output.startswith("'") and raw_output.endswith("'")) or (
                    raw_output.startswith('"') and raw_output.endswith('"')
                ):
                    raw_output = raw_output[1:-1]
                st.markdown(raw_output)
                st.session_state.messages.append({"role": "assistant", "content": raw_output})
            else:
                st.error(f"An error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})


with st.sidebar:
    st.header("Configuration")

    if "db_user" not in st.session_state:
        st.session_state.db_user = os.getenv("DB_USER", "user")
    if "db_password" not in st.session_state:
        st.session_state.db_password = os.getenv("DB_PASSWORD", "password")
    if "db_host" not in st.session_state:
        st.session_state.db_host = os.getenv("DB_HOST", "localhost")
    if "db_port" not in st.session_state:
        st.session_state.db_port = os.getenv("DB_PORT", "5432")
    if "db_name" not in st.session_state:
        st.session_state.db_name = os.getenv("DB_NAME", "chinook")

    with st.form("api_config_form"):
        default_api_key = os.getenv("GOOGLE_API_KEY", st.session_state.get("api_key", ""))
        api_key = st.text_input("Enter your Google API Key:", value=default_api_key, type="password")
        
        current_api_key = st.session_state.get("api_key", default_api_key)
        model_names = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]
        
        if current_api_key:
            try:
                genai.configure(api_key=current_api_key)
                models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
                if models:
                    model_names = [m.split("/")[1] for m in models]
            except Exception:
                pass
        
        default_model = st.session_state.get("model_name", "gemini-1.5-flash")
        if default_model not in model_names:
            default_model = model_names[0] if model_names else "gemini-1.5-flash"
            
        model_name = st.selectbox("Select a model:", model_names, index=model_names.index(default_model))
        
        submit_api = st.form_submit_button("Save API Configuration")
        if submit_api:
            st.session_state.api_key = api_key
            st.session_state.model_name = model_name
            st.success("API Configuration saved!")
            st.rerun()

    st.divider()
    with st.expander("Database Configuration", expanded=False):
        db_user = st.text_input("DB User:", value=st.session_state.db_user)
        db_password = st.text_input("DB Password:", value=st.session_state.db_password, type="password")
        db_host = st.text_input("DB Host:", value=st.session_state.db_host)
        db_port = st.text_input("DB Port:", value=st.session_state.db_port)
        db_name = st.text_input("DB Name:", value=st.session_state.db_name)

        if st.button("Save DB Configuration"):
            st.session_state.db_user = db_user
            st.session_state.db_password = db_password
            st.session_state.db_host = db_host
            st.session_state.db_port = db_port
            st.session_state.db_name = db_name
            st.success("DB Configuration saved!")

    if st.button("Start New Chat"):
        st.session_state.messages = []
        st.rerun()

st.header("Conversation")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "api_key" in st.session_state and st.session_state.api_key and "model_name" in st.session_state:
    db_uri = get_db_uri()
    agent_executor = get_agent_executor(db_uri, st.session_state.model_name, st.session_state.api_key)

    if prompt := st.chat_input("Ask a question about the Chinook database:"):
        handle_chat(agent_executor, prompt)
else:
    st.warning("Please configure your API key and model in the sidebar.")
