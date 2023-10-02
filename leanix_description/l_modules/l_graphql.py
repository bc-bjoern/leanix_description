"""
This module facilitates communication with the LeanIX GraphQL API
to add comments to Fact Sheets.

Attributes:
    requests.exceptions.RequestException: An exception class from the `requests` library.

Classes:
    LeanIxGraphQL: A class for communicating with the LeanIX GraphQL API and adding comments to Fact Sheets.
"""

import json
import requests

class LeanIxGraphQL:
    """
    This class facilitates communication with the LeanIX GraphQL API
    to add comments to Fact Sheets.
    """

    def __init__(self, auth_url, api_token, request_url):
        """
        Initializes an instance of the LeanIxGraphQL class.

        Args:
            auth_url (str): The URL to the authentication endpoint.
            api_token (str): The API token for authentication.
            request_url (str): The URL for GraphQL requests.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        try:
            response = requests.post(
                auth_url,
                timeout=30,
                auth=('apitoken', api_token),
                data={'grant_type': 'client_credentials'}
            )
            response.raise_for_status()
            self.access_token = response.json()['access_token']
            self.request_url = request_url
        except requests.exceptions.RequestException as exception:
            raise RuntimeError(f"Failed to initialize LeanIxGraphQL: {exception}")

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

            response = requests.post(url=self.request_url, headers=header, data=json_post, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as exception:
            raise RuntimeError(f"Failed to send mutation to LeanIX: {exception}")
