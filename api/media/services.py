# System Utils
import base64
import requests
from django.conf import settings

class Imgur():
    def upload(self, image):
        # Set the Imgur's Client ID
        authorization_header = f"Client-ID {settings.IMGUR_CLIENT_ID}"

        try:

            # Read the file content into a byte array
            file_bytes = image.read()

            # Convert the byte array to a base64-encoded string
            base64_string = base64.b64encode(file_bytes).decode('utf-8')

            # Prepare the data for the request
            data = {
                'image': base64_string
            }

            # Set the headers for the request
            headers = {
                'Authorization': authorization_header
            }

            # Send request to Imgur
            response = requests.post('https://api.imgur.com/3/image', data=data, headers=headers)

            # Handle the response
            response_json = response.json()

            # Handle the response
            if 'status' in response_json and response_json['status'] == 200:
                # The upload was successful
                return {
                    'success': True,
                    'data': response_json['data']
                }
            else:
                # There was an error
                error_message = response_json['data']['error']
                return {
                    'success': False,
                    'error': f"Error: {error_message}"
                }
            
        except Exception as e:
            # Handle any other errors that might occur
            return {
                'success': False,
                'error': f"An unexpected error occurred: {str(e)}"
            }