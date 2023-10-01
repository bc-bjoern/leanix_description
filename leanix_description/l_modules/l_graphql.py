import json
import requests

class LeanIX_GraphQL:
    """
    This class facilitates communication with the LeanIX GraphQL API
    to add comments to Fact Sheets.
    """

    def __init__(self, AUTH_URL, API_TOKEN, REQUEST_URL):
        """
        Initializes an instance of the LeanIX_GraphQL class.

        Args:
            AUTH_URL (str): The URL to the authentication endpoint.
            API_TOKEN (str): The API token for authentication.
            REQUEST_URL (str): The URL for GraphQL requests.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        try:
            response = requests.post(
                AUTH_URL,
                auth=('apitoken', API_TOKEN),
                data={'grant_type': 'client_credentials'}
            )
            response.raise_for_status()
            self.access_token = response.json()['access_token']
            self.request_url = REQUEST_URL
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to initialize LeanIX_GraphQL: {e}")

    def add_comment(self, factsheet_id, factsheet_comment):
        """
        Adds a comment to a Fact Sheet.

        Args:
            factsheet_id (str): The ID of the Fact Sheet to which the comment should be added.
            factsheet_comment (str): The text of the comment.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        mutation_string = """
            mutation {
              createComment(factSheetId: "%s", message: "%s", status: ACTIVE) {
                id
              }
            }
          """ % (factsheet_id, factsheet_comment)

        self.send_mutation(mutation_string)

    def send_mutation(self, mutation_string):
        """
        Sends a GraphQL mutation request to the LeanIX API.

        Args:
            mutation_string (str): The GraphQL mutation request as a string.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        try:
            data_mutation = {"query": str(mutation_string)}
            json_post = json.dumps(data_mutation)
            auth_header = 'Bearer ' + self.access_token
            header = {'Authorization': auth_header}

            response = requests.post(url=self.request_url, headers=header, data=json_post)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to send mutation to LeanIX: {e}")
