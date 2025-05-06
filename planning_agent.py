import os
import json
import logging
import uuid
import requests
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import ValidationError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import A2A models
try:
    from a2a_models import (
        SendTaskRequest, SendTaskResponse, Task, TaskStatus, TaskState, Message, TextPart, JSONRPCError, JSONRPCResponse, Part, TaskSendParams
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

# Execution Agent Server URL
EXECUTION_AGENT_URL = "http://localhost:5000/a2a/tasks/send"

# Planning Agent System Prompt
PLANNING_AGENT_SYSTEM_PROMPT = """You are a Planning Agent designed to break down complex tasks and orchestrate their execution by communicating with an Execution Agent via the A2A protocol.
Your role is to analyze the user's goal, determine the necessary steps, formulate clear instructions for the Execution Agent, and process the Execution Agent's responses to guide the task to completion.
You will receive the full task history in each response from the Execution Agent. Use this history to understand the current state and decide on the next instruction.
When the task is complete, indicate this in your response.
"""

def send_a2a_request(request_payload: SendTaskRequest) -> Optional[SendTaskResponse]:
    """Sends an A2A request to the Execution Agent and returns the response."""
    logger.info(f"Sending A2A request to {EXECUTION_AGENT_URL}")
    payload_dict = request_payload.model_dump(exclude_none=True)
    logger.info(f"Request Payload: {json.dumps(payload_dict, indent=2)}")

    # Log the raw request payload to the communication log
    with open("communication_log.txt", "a") as f:
        f.write("--- Planning Agent Sent Request ---\n")
        f.write(json.dumps(payload_dict, indent=2))
        f.write("\n-------------------------------------\n")

    try:
        response = requests.post(EXECUTION_AGENT_URL, json=payload_dict)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        response_payload = response.json()
        logger.info(f"Received A2A response: {json.dumps(response_payload, indent=2)}")

        # Log the raw response payload to the communication log
        with open("communication_log.txt", "a") as f:
            f.write("--- Planning Agent Received Response ---\n")
            f.write(json.dumps(response_payload, indent=2))
            f.write("\n----------------------------------------\n")

        # Validate the response payload
        send_task_response = SendTaskResponse(**response_payload)
        if send_task_response.error:
            logger.error(f"Received error in A2A response: {send_task_response.error}")
            return None # Indicate error
        return send_task_response

    except ValidationError as e:
        logger.error(f"Response validation failed: {e.errors()}", exc_info=True)
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending A2A request: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during A2A communication: {e}", exc_info=True)
        return None

def plan_and_execute_task(user_goal: str):
    """Manages the task planning and execution flow."""
    task_id = str(uuid.uuid4())
    logger.info(f"Starting new task with ID: {task_id}")

    current_task: Optional[Task] = None
    turn_count = 0
    max_turns = 5 # Limit turns for demo purposes

    while turn_count < max_turns:
        turn_count += 1
        logger.info(f"--- Turn {turn_count} ---")

        # Determine the message to send to the Execution Agent
        if turn_count == 1:
            # Initial message based on the user goal
            message_content = user_goal
            message_role = "user" # Message from Planning Agent to Execution Agent is "user" role
            logger.info(f"Turn 1: Sending initial user goal to Execution Agent.")
        else:
            # Subsequent messages based on Planning Agent's LLM analysis of the response
            if current_task and current_task.history:
                # Use the Planning Agent LLM to decide the next step
                planning_prompt = f"""{PLANNING_AGENT_SYSTEM_PROMPT}

Current Task ID: {task_id}
Task History:
{json.dumps([msg.model_dump(exclude_none=True) for msg in current_task.history], indent=2)}

Analyze the task history and the user's original goal: "{user_goal}".
Determine the next instruction for the Execution Agent.
If the task is complete based on the history, respond with "TASK_COMPLETE".
Otherwise, provide the next instruction as a plain text message for the Execution Agent.
"""
                logger.info(f"Sending planning prompt to LLM for Task ID {task_id}, Turn {turn_count}.")
                next_instruction = "Error: LLM not configured or generated no text."
                if genai_client:
                    try:
                        llm_response = genai_client.generate_content(
                             contents=[
                                {"role": "user", "parts": [{"text": planning_prompt}]}
                            ]
                        )
                        if hasattr(llm_response, 'text'):
                            next_instruction = llm_response.text.strip()
                            logger.info(f"Planning LLM generated instruction: '{next_instruction[:100]}...'")
                        else:
                            next_instruction = str(llm_response).strip()
                            logger.warning(f"Planning LLM response has no text attribute. Using string representation: {next_instruction[:100]}...")

                    except Exception as e:
                        logger.error(f"Error during Planning LLM processing for Task ID {task_id}: {e}", exc_info=True)
                        next_instruction = f"Error: Planning LLM failed - {e}"
                else:
                    logger.warning("Gemini client not initialized. Cannot use Planning LLM.")


                if next_instruction == "TASK_COMPLETE":
                    logger.info(f"Planning Agent determined task {task_id} is complete.")
                    break # Exit the loop if task is complete

                message_content = next_instruction
                message_role = "user" # Message from Planning Agent to Execution Agent is "user" role
                logger.info(f"Turn {turn_count}: Sending next instruction to Execution Agent.")

            else:
                logger.error(f"Task history is empty or None for Task ID {task_id} after turn 1. Cannot continue.")
                break # Exit if history is unexpectedly empty

        # Construct the A2A Message
        text_part = TextPart(text=message_content)
        user_a2a_message = Message(
            role=message_role,
            parts=[text_part]
        )

        # Construct the A2A SendTaskRequest
        task_send_params = TaskSendParams(
            id=task_id,
            message=user_a2a_message
        )
        send_request = SendTaskRequest(
            jsonrpc="2.0",
            id=str(uuid.uuid4()), # Use a new JSON-RPC request ID for each request
            params=task_send_params
        )

        # Send the request and get the response
        response = send_a2a_request(send_request)

        if response and response.result:
            current_task = response.result
            logger.info(f"Received updated Task object for ID {task_id}. Status: {current_task.status.state}")
            # Log the full task history received
            if current_task and current_task.history is not None:
                logger.info(f"Full Task History Received:\n{json.dumps([msg.model_dump(exclude_none=True) for msg in current_task.history], indent=2)}")
            else:
                logger.info("Full Task History Received: None or empty.")

            # Add a small delay before the next turn
            time.sleep(1)
        elif response and response.error:
             logger.error(f"Received error response for Task ID {task_id}: {response.error}")
             break # Stop if an error is received
        else:
            logger.error(f"No valid response received for Task ID {task_id}.")
            break # Stop if no valid response

    logger.info(f"Task {task_id} finished after {turn_count} turns.")
    if current_task:
        logger.info(f"Final Task Status: {current_task.status.state}")
        if current_task and current_task.history is not None:
            logger.info(f"Final Task History:\n{json.dumps([msg.model_dump(exclude_none=True) for msg in current_task.history], indent=2)}")
        else:
            logger.warning("No final task history available.")
    else:
        logger.warning(f"No final task object available for Task ID {task_id}.")


if __name__ == '__main__':
    # Ensure communication_log.txt exists or is cleared for a new run
    # This is also done by the execution agent, but doing it here ensures it's clear
    if os.path.exists("communication_log.txt"):
        os.remove("communication_log.txt")
    # Create an empty log file
    open("communication_log.txt", "w").close()
    logger.info("communication_log.txt initialized by Planning Agent.")

    # Example user goal
    example_goal = "Tell me a short, funny story about a robot chef."
    plan_and_execute_task(example_goal)
