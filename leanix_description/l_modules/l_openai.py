"""
This module facilitates communication with the OpenAI GPT model
to generate descriptions for applications.

Attributes:
    openai.ChatCompletion: A class from the OpenAI Python library for generating text completions.

Classes:
    OpenAiChatGPT: A class for communicating with the OpenAI GPT model and generating descriptions.
"""

import html
import openai
import requests

class OpenAiChatGPT:
    """
    This class facilitates communication with the OpenAI GPT model
    to generate descriptions for applications.
    """

    def __init__(self, openai_model, openai_max_tokens, openai_api_key):
        """
        Initializes an instance of the OpenAiChatGPT class.

        Args:
            openai_model (str): The OpenAI model name or identifier.
            openai_max_tokens (int): The maximum number of tokens for model responses.
            openai_api_key (str): The API key for authenticating with OpenAI.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        self.openai_model = openai_model
        self.openai_max_tokens = openai_max_tokens
        self.openai_api_key = openai_api_key

    def generate_description(self, app_name, openai_challenge):
        """
        Generates a description for an application using the OpenAI GPT model.

        Args:
            app_name (str): The name of the application for which the description is generated.

        Returns:
            str: The generated description for the application.
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[{"role": "system", "content": openai_challenge + app_name}],
                max_tokens=self.openai_max_tokens,
                stop=None,
                api_key=self.openai_api_key
            )

            text = response.choices[0].message.content.strip()
            last_period_index = text.rfind(".")

            if last_period_index != -1:
                cropped_text = text[:last_period_index + 1]

            # For some reasons GraphQL API don't accept the text from openai without manipulation
            # The "\n"-Signs especially seems to be a issue. Since there are no returns, it's hard to debug it.
            # If someone know to do it pretty - feel free to fix it.
            decoded_string = html.unescape(cropped_text)  # Decode HTML entities
            decoded_string = decoded_string.replace("\n", " ") # Don't ask me...
            return decoded_string
        except Exception as exception:
            raise RuntimeError(f"Failed to generate description using OpenAI: {exception}")
