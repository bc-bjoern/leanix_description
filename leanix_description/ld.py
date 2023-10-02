#!/usr/bin/env python3
"""
This is a LeanIX Description Bot for automatically generating and adding descriptions
to LeanIX Fact Sheets using OpenAI's GPT-3.5 model.

The bot listens for FactSheetCreatedEvents via a webhook and generates a description for
the newly created Fact Sheet, then adds it as a comment in LeanIX.

Configuration is provided through environment variables.

Required Environment Variables:
- ACTIVE: Set to 1 to activate the bot.
- OPENAI_API_KEY: Your OpenAI API key.
- OPENAI_MODEL: The OpenAI model to use (default is 'gpt-3.5-turbo').
- OPENAI_MAX_TOKENS: The maximum number of tokens for OpenAI responses (default is 200).
- USERNAME: Your LeanIX Basic Auth username.
- PASSWORD: Your LeanIX Basic Auth password.
- API_TOKEN: Your LeanIX API token.
- AUTH_URL: The URL for LeanIX authentication.
- REQUEST_URL: The URL for GraphQL requests in LeanIX.
- HOST: The host to run the Flask app (default is '0.0.0.0').
- PORT: The port to run the Flask app (default is 5000).
- DEBUG: Set to True for debugging (default is False).
- ALLOWED_FACTSHEETS: Comma-separated list of Fact Sheet types to process (default is 'Application').
- ALLOWED_USER_AGENTS: Comma-separated list of allowed User-Agent values.

This bot uses the Flask framework and Flask-Limiter for rate limiting.
"""

from functools import wraps
from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from decouple import config, Csv
from l_modules import l_graphql
from l_modules import l_openai

# Turn it on or off
ACTIVE = config('ACTIVE', default=1, cast=int)

# OpenAI challenge
openai_challenge = config('OPENAI_CHALLENGE', default='Erstelle eine Beschreibung für die Applikation namens')
# OpenAI API Key
openai_api_key = config('OPENAI_API_KEY', default='')
# OpenAI Model
openai_model = config('OPENAI_MODEL', default='gpt-3.5-turbo')
# OpenAI Max answer chars
openai_max_tokens = config('OPENAI_MAX_TOKENS', default=200, cast=int)

# Leanix Basic Auth Data
USERNAME = config('USERNAME', default='')
PASSWORD = config('PASSWORD', default='')
# Leanix API User Key
api_token = config('API_TOKEN', default='')
# LeanIX Auth URL
auth_url = config('AUTH_URL', default='')
# LeanIX Request URL
request_url = config('REQUEST_URL', default='')

# Flask Interface
host = config('HOST', default='0.0.0.0')
port = config('PORT', default=5000, cast=int)
debug = config('DEBUG', default=False, cast=bool)

# LeanIX Description Bot
allowed_factsheets = config('ALLOWED_FACTSHEETS', default='Application')

# Allowed user agents
allowed_user_agents = config('ALLOWED_USER_AGENTS', default='', cast=Csv())

# Initialize Flask app
app = Flask(__name__)

# Initialize Limiter for rate limiting
limiter = Limiter(app)

# helper function to handle errors
def handle_error(error, status_code):
    """
    Handles errors by printing the error message and generating an appropriate JSON response.

    Args:
        error (Exception): The exception or error that occurred.
        status_code (int): The HTTP status code to include in the response.

    Returns:
        Response: A JSON response with an error message and the specified status code.
    """
    print(f"An error occurred: {str(error)}")
    return abort_with_message("An error occurred.", status_code)

# helper to print errors
def abort_with_message(message, status_code=400):
    """
    Generates a JSON response with a custom error message and status code for aborting a request.

    Args:
        message (str): The error message to include in the response.
        status_code (int, optional): The HTTP status code to use (default is 400).

    Returns:
        Response: A JSON response with the provided message and status code.
    """
    return jsonify({'message': message}), status_code

# Function to check Basic Auth Header
def check_auth(username, password):
    """
    Checks if the provided username and password match the configured LeanIX Basic Auth credentials.

    Args:
        username (str): The username to be checked.
        password (str): The password to be checked.

    Returns:
        bool: True if the provided credentials match, False otherwise.
    """
    return username == USERNAME and password == PASSWORD

# Function to handle authentication
def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    message = {'message': "Authentication required."}
    return jsonify(message), 401, {'WWW-Authenticate': 'Basic realm="Login required"'}

# Decorator-Function for authentication
def requires_auth(func):
    """
    Decorator function for enforcing basic authentication on Flask routes.

    This decorator checks if the request has valid Basic Authentication credentials
    by comparing them with the configured LeanIX Basic Auth credentials.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function if authentication is successful,
        or a 401 Unauthorized response if authentication fails.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return func(*args, **kwargs)
    return decorated

# Apply rate limiting to the webhook_handler function
@limiter.limit("10 per minute")  # Adjust the rate limit as needed
@app.route('/webhook', methods=['POST'])
@requires_auth
def webhook_handler():
    """
    Handle incoming webhook requests from LeanIX.

    This function processes incoming POST requests to the '/webhook' route.
    It performs the following checks:
    - Validates the User-Agent header against allowed user agents.
    - Ensures the request is from LeanIX by checking the X-Webhooks-Event header.
    - Parses and processes FactSheetCreatedEvent webhooks for allowed fact sheet types.
    - Utilizes OpenAI's ChatGPT to generate comments for fact sheets and adds them via LeanIX GraphQL.

    Returns:
        Response: A JSON response indicating the success or failure of the webhook handling.
    """
    user_agent = request.headers.get('User-Agent')
    # Check user agent
    if user_agent not in allowed_user_agents:
        abort_with_message("User-Agent is forbidden.", 403)

    # Check if request is from LeanIX
    if 'X-Webhooks-Event' not in request.headers:
        abort_with_message("No official request.", 403)

    webhook_event = request.headers.get('X-Webhooks-Event')
    if 'leanix.net' not in webhook_event:
        abort_with_message("No official request.", 403)

    try:
        data = request.json
        event_type = data.get('type')
        factsheet_id = data['factSheet']['id']
        factsheet_name = data['factSheet']['name']
        factsheet_type = data['factSheet']['type']

        if event_type == 'FactSheetCreatedEvent' and factsheet_type in allowed_factsheets:
            if factsheet_id and ACTIVE == 1:
                openai = l_openai.OpenAiChatGPT(openai_model, openai_max_tokens, openai_api_key)
                factsheet_comment = openai.generate_description(factsheet_name, openai_challenge)
                comment = 'Hier ist ein Vorschlag für eine Beschreibung: ' + factsheet_comment
                leanix = l_graphql.LeanIxGraphQL(auth_url, api_token, request_url)
                leanix.add_comment(factsheet_id, comment)
            else:
                print("Turned off")

            return jsonify({'message': 'Webhook successful'}), 200

        abort_with_message("Webhook wrong.")
    except FileNotFoundError as file_error:
        return handle_error(file_error, 404)
    except PermissionError as permission_error:
        return handle_error(permission_error, 403)
    except requests.exceptions.RequestException as request_error:
        return handle_error(request_error, 500)

    return None

if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug)
