"""
A module that provides a helper class 'GPT' for working with GPT models using
the OpenAI API. The class includes methods for calculating tokens, constructing
GPT payloads, and sending GPT payloads to the API based on the contents of a
Notion page.
"""
import json
from enum import Enum
from typing import Dict, List, Tuple, Any

import openai

class GPTException(Exception):
    """Custom exception for GPT-related errors."""


class GPTModel(Enum):
    """
    Enumeration of GPT models with their respective IDs and token limits.
    """

    CHAT_GPT = ("gpt-3.5-turbo", 4096)
    CHAT_GPT_16K = ("gpt-3.5-turbo-16k", 16384)
    GPT_4 = ("gpt-4", 8192)
    GPT_4_32K = ("gpt-4-32k", 32768)

    def __new__(cls, _id: str, limit: int):
        """Create custom Enum object"""
        obj = object.__new__(cls)
        obj.id = _id
        obj.limit = limit
        return obj


class GPT:
    """
    A helper class for working with GPT models using the OpenAI API.
    The class includes methods for calculating tokens, constructing GPT payloads,
    and sending GPT payloads to the API based on the contents of a Notion page.
    """

    SYSTEM_MESSAGE = """
    You are AssistantGPT. You collect input from a user in terms of things they need to do, then use create_task function to create tasks.
            For 'priority' parameter, you use 1 for the highest priority, 4 for the lowest priority, and 0 for no priority.
            For 'due_date' you calculate it using 'calculate_date' function first, then use its output in 'create_task' function's 'due_date' parameter.

            For example, if a user says "I have a meeting tomorrow at 9AM", you first call 'calculate_date' with 'days' set to 1 and 'hours' set to 9. 
            'calculate_date' will output a unix timestamp. Then you call 'create_task' function with the outputted unix timestamp in 'due_date' parameter.

            NEVER ask follow up questions. First always create all tasks before sending the final response. Make best judgements from the context.
    """

    def __init__(self, available_functions: Dict[str, Any]):
        self.available_functions = available_functions

    def converse(self, transcript: str) -> str:
        """
        Converse with the chatbot by sending recognized transcript.

        Args:
            transcript (str): recognized transcript.

        Returns:
            str: The response message from the chatbot.
        """
        messages = [
            {"role": "system", "content": GPT.SYSTEM_MESSAGE},
            {"role": "user", "content": transcript},
        ]
        while True:
            response = self._send_gpt_payload(messages, model=GPTModel.GPT_4)
            response_message = response["choices"][0]["message"]
            messages.append(response_message)
            # If the response is a function call
            if response_message.get("function_call"):
                (function_name, function_output) = self._process_function_call(
                    response_message
                )
                messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_output,
                    }
                )
            else:
                break
        return response_message['content']

    def _send_gpt_payload(self, messages: List[Dict[str, str]], model: GPTModel):
        """
        Send a list of message payloads to the GPT API.

        Args:
            messages: List of message payloads (e.g., [{'role': 'user', 'content': 'Hello'}])
            model: The GPT model to send the payloads to.

        Returns:
            str: The assistant's response from the GPT API.
        """
        function_definitions = list(self.available_functions.values())
        response = openai.ChatCompletion.create(
            model=model.id, functions=function_definitions, messages=messages
        )
        return response

    def _process_function_call(self, response: Dict[str, str]) -> Tuple[str, Any]:
        """
        Process a function call request from the GPT response.

        Args:
            response (Dict[str, str]): The response dictionary containing the function call request.

        Returns:
            Tuple[str, Any]: A tuple containing the function name and its output.

        Raises:
            GPTException: If the response does not contain a function call request
                or if the function is not available.
        """
        if "function_call" not in response:
            raise GPTException("This is not a function call request")

        function_call = response["function_call"]
        function_name = function_call["name"]

        for call in self.available_functions.keys():
            if call.__name__ == function_name:
                function_args = json.loads(function_call["arguments"])
                function_output = call(**function_args)
                return function_name, function_output

        raise GPTException(f"There is no {function_name} function available")
