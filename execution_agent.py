import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List

from a2a_models import Part # Explicitly import Part for type hinting

from flask import Flask, request, jsonify
from pydantic import ValidationError
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import A2A models
try:
    from a2a_models import (
        SendTaskRequest, SendTaskResponse, Task, TaskStatus, TaskState, Message, TextPart, JSONRPCError, JSONRPCResponse
    )
    logger.info("Successfully imported A2A models.")
except ImportError as e:
    logger.error(f"Error importing A2A models: {e}")
    # Exit or handle the error appropriately if models cannot be imported

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables.")
    # In a real app, you might raise an exception or exit
    # For this demo, we'll proceed but LLM calls will fail
    genai_client = None
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use the specified model
        genai_client = genai.GenerativeModel('gemini-1.5-flash-latest')
        logger.info("Successfully configured Gemini client with gemini-1.5-flash-latest.")
    except Exception as e:
        logger.error(f"Error configuring Gemini client: {e}")
        genai_client = None

app = Flask(__name__)

# In-memory task storage
tasks: Dict[str, Task] = {}

# Execution Agent System Prompt
EXECUTION_AGENT_SYSTEM_PROMPT = """You are an Execution Agent designed to fulfill specific instructions provided by a Planning Agent.
Your role is to directly execute the task described in the latest user message and provide a concise response.
Do not engage in planning or complex reasoning. Focus solely on generating the output requested by the Planning Agent.
Your response will be used as a message back to the Planning Agent.
"""

@app.route('/a2a/tasks/send', methods=['POST'])
def send_task():
    """Handles incoming A2A tasks/send requests."""
    logger.info(f"Received POST request at /a2a/tasks/send")
    request_payload = request.get_json()
    logger.info(f"Request Payload: {json.dumps(request_payload, indent=2)}")

    # Log the raw request payload to the communication log
    with open("communication_log.txt", "a") as f:
        f.write("--- Execution Agent Received Request ---\n")
        f.write(json.dumps(request_payload, indent=2))
        f.write("\n----------------------------------------\n")

    try:
        # Validate the request payload
        send_task_request = SendTaskRequest(**request_payload)
        task_params = send_task_request.params
        task_id = task_params.id
        user_message = task_params.message

        logger.info(f"Validated request for Task ID: {task_id}")

        # Retrieve or initialize the task
        task = tasks.get(task_id)
        if task is None:
            logger.info(f"Task ID {task_id} not found. Creating new task.")
            task = Task(
                id=task_id,
                status=TaskStatus(state=TaskState.submitted),
                history=[]
            )
            tasks[task_id] = task
        else:
            logger.info(f"Task ID {task_id} found. Appending new message.")
            # Ensure history is a list before appending
            if task.history is None:
                task.history = []

        # Append the user message (from the Planning Agent) to history
        task.history.append(user_message)
        task.status.state = TaskState.working
        task.status.timestamp = datetime.utcnow().isoformat()

        logger.info(f"Task {task_id} history updated. Current history length: {len(task.history or [])}")

        # Process the latest message using the LLM
        agent_response_text = "Error: LLM not configured."
        if genai_client:
            try:
                # Get the latest user message content
                latest_user_message_content = ""
                if user_message.parts:
                    # Process all text parts in the message
                    text_parts_content = []
                    for part in user_message.parts:
                        if isinstance(part, TextPart):
                            text_parts_content.append(part.text)
                        else:
                            logger.warning(f"Skipping non-text part of type: {type(part)}")
                    latest_user_message_content = "\n".join(text_parts_content)

                logger.info(f"Sending combined user message content to LLM: '{latest_user_message_content[:100]}...'")

                # Create the conversation history for the LLM, including the system prompt
                # Note: Gemini's history format is different from A2A's.
                # For this simple demo, we'll just send the latest message with the system prompt.
                # A more complex agent might convert the A2A history to the LLM's format.

                # For a simple echo task, we can just echo the text
                # For an LLM task, we'd call the LLM here
                # For this demo, let's use the LLM to process the request based on the prompt
                llm_response = genai_client.generate_content(
                    contents=[
                        {"role": "user", "parts": [{"text": EXECUTION_AGENT_SYSTEM_PROMPT + "\n\n" + latest_user_message_content}]}
                    ]
                )

                if hasattr(llm_response, 'text'):
                    agent_response_text = llm_response.text
                    logger.info(f"LLM generated response (text): '{agent_response_text[:100]}...'")
                else:
                     agent_response_text = str(llm_response)
                     logger.warning(f"LLM response has no text attribute. Using string representation: {agent_response_text[:100]}...")


            except Exception as e:
                logger.error(f"Error during LLM processing for Task ID {task_id}: {e}", exc_info=True)
                agent_response_text = f"Error processing message with LLM: {e}"
        else:
             logger.warning("Gemini client not initialized. Cannot process LLM request.")


        # Create the agent's response message
        text_part = TextPart(text=agent_response_text)
        agent_parts: List[Part] = [text_part]
        agent_message = Message(
            role="agent",
            parts=agent_parts
        )

        # Append the agent's response to history
        if task.history is None:
            task.history = []
        task.history.append(agent_message)

        # Update task status to completed for this turn
        task.status.state = TaskState.completed
        task.status.timestamp = datetime.utcnow().isoformat()
        task.status.message = agent_message # Set the final message for this turn

        logger.info(f"Task {task_id} completed for this turn.")

        # Construct the A2A response
        response_payload = SendTaskResponse(
            jsonrpc="2.0",
            id=send_task_request.id, # Use the same ID as the request
            result=task
        ).model_dump(exclude_none=True) # Use model_dump for Pydantic v2

        logger.info(f"Sending Response Payload for Task ID {task_id}: {json.dumps(response_payload, indent=2)}")

        # Log the raw response payload to the communication log
        with open("communication_log.txt", "a") as f:
            f.write("--- Execution Agent Sent Response ---\n")
            f.write(json.dumps(response_payload, indent=2))
            f.write("\n---------------------------------------\n")

        return jsonify(response_payload)

    except ValidationError as e:
        logger.error(f"Request validation failed: {e.errors()}", exc_info=True)
        error_response = JSONRPCResponse(
            jsonrpc="2.0",
            id=request_payload.get('id'), # Use the request ID if available
            error=JSONRPCError(code=-32602, message="Invalid parameters", data={"details": str(e.errors())})
        ).model_dump(exclude_none=True)
        return jsonify(error_response), 400 # Bad Request

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        error_response = JSONRPCResponse(
            jsonrpc="2.0",
            id=request_payload.get('id'), # Use the request ID if available
            error=JSONRPCError(code=-32603, message="Internal error", data={"details": str(e)})
        ).model_dump(exclude_none=True)
        return jsonify(error_response), 500 # Internal Server Error

if __name__ == '__main__':
    # Ensure communication_log.txt exists or is cleared for a new run
    if os.path.exists("communication_log.txt"):
        os.remove("communication_log.txt")
    # Create an empty log file
    open("communication_log.txt", "w").close()
    logger.info("communication_log.txt initialized.")

    # Run the Flask app
    # Use a specific port, e.g., 5000
    app.run(port=5000, debug=True, use_reloader=False) # use_reloader=False to avoid running twice
