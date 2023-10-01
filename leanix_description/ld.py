#!/usr/bin/env python3
from flask import Flask, request, jsonify, abort
from functools import wraps
import base64
import requests
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
API_TOKEN = config('API_TOKEN', default='')
# LeanIX Auth URL
AUTH_URL = config('AUTH_URL', default='')
# LeanIX Request URL
REQUEST_URL = config('REQUEST_URL', default='')

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

# Function to check Basic Auth Header
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

# Function to handle authentication
def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    message = {'message': "Authentication required."}
    return jsonify(message), 401, {'WWW-Authenticate': 'Basic realm="Login required"'}

# Decorator-Function for authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Apply rate limiting to the webhook_handler function
@limiter.limit("10 per minute")  # Adjust the rate limit as needed
@app.route('/webhook', methods=['POST'])
@requires_auth
def webhook_handler():
    user_agent = request.headers.get('User-Agent')
    # Check user agent
    if user_agent not in allowed_user_agents:
        print(user_agent + " is forbidden.")
        abort(403)

    # Check if request is from LeanIX
    if 'X-Webhooks-Event' not in request.headers:
        print("No official request")
        abort(403)

    webhook_event = request.headers.get('X-Webhooks-Event')
    if 'leanix.net' not in webhook_event:
        print("No official request")
        abort(403)

    try:
        data = request.json
        workspace_id = data.get('workspaceId')
        user_id = data.get('userId')
        event_type = data.get('type')
        factsheet_id = data['factSheet']['id']
        factsheet_name = data['factSheet']['name']
        factsheet_type = data['factSheet']['type']

        if event_type == 'FactSheetCreatedEvent' and factsheet_type in allowed_factsheets:
            if factsheet_id and ACTIVE == 1:
                openai = l_openai.OpenAI_ChatGPT(openai_model, openai_max_tokens, openai_api_key)
                factsheet_comment = openai.generate_description(factsheet_name, openai_challenge)
                preface = "Hier ist ein Vorschlag für eine Beschreibung: "
                comment = preface + factsheet_comment
                leanix = l_graphql.LeanIX_GraphQL(AUTH_URL, API_TOKEN, REQUEST_URL)
                leanix.add_comment(factsheet_id, comment)
            else:
                print("Turned off")

            return jsonify({'message': 'Webhook successful'}), 200

        return "Webhook wrong."
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        abort(500)

if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug)
