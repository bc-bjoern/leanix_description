import openai
import requests
import html

class OpenAI_ChatGPT:
    """
    This class facilitates communication with the OpenAI GPT model
    to generate descriptions for applications.
    """

    def __init__(self, openai_model, openai_max_tokens, openai_api_key):
        """
        Initializes an instance of the OpenAI_ChatGPT class.

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

            decoded_string = html.unescape(cropped_text)  # Decode HTML entities

            return decoded_string
        except Exception as e:
            raise RuntimeError(f"Failed to generate description using OpenAI: {e}")
