import ssl

import aiohttp
import cv2
from aiohttp import FormData, ClientTimeout


class WebRequest:
    def __init__(self, api_url, api_key):
        """
        Initializes the WebRequest class for handling web requests.

        Args:
            api_url (str): Base URL of the API endpoint.
            api_key (str): Bearer token for API authentication.
        """
        self.api_url = api_url.rstrip('/')  # Ensure no trailing slash
        self.api_key = api_key

        self.client_timeout = ClientTimeout(total=30)

        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def _send_post_request(self, endpoint, data, headers):
        """
        Sends a POST request to the API.

        Args:
            endpoint (str): API endpoint to send the request to.
            data (FormData): FormData object containing the request payload.
            headers (dict): Dictionary of request headers.

        Returns:
            dict: Response from the API in JSON format, or None if failed.
        """
        try:

            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                async with session.post(f'{self.api_url}/{endpoint}', data=data, headers=headers, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        return await response.json()  # Return the response JSON
                    else:
                        print(f"API request failed with status {response.status}")
                        return None
        except Exception as e:
            print(f"Error during API request.\n -> {e}")
            return None

    async def upload_image(self, image, filename='face.jpg'):
        """
        Uploads an image to the API.

        Args:
            image: Image (NumPy array) to upload.
            filename (str): Filename for the image.

        Returns:
            str: Image ID returned by the API, or None if failed.
        """
        # Encode image to JPEG format
        success, img_encoded = cv2.imencode('.jpg', image)

        if not success:
            print("Failed to encode image.")
            return None

        # Create the multipart form data to send the image
        form = FormData()
        form.add_field('file', img_encoded.tobytes(), content_type='image/jpeg', filename=filename)

        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

        # Send the POST request to upload the image
        response = await self._send_post_request('v1/Images/upload', form, headers)

        if response:
            return response.get('id')  # Assuming the response contains an 'id' field for the image
        return None

    async def delete_image(self, image_id):
        """
        Deletes an image by its ID from the API.

        Args:
            image_id (str): ID of the image to delete.

        Returns:
            bool: True if the image was deleted, False otherwise.
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

        try:
            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                async with session.delete(f'{self.api_url}/v1/Images/{image_id}', headers=headers, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        print(f"Image with ID {image_id} deleted successfully.")
                        return True
                    else:
                        print(f"Failed to delete image with ID {image_id}: {response.status}")
                        return False
        except Exception as e:
            print(f"Error deleting image.\n -> {e}")
            return False

    async def get_image_info(self, image_id):
        """
        Retrieves information about an image from the API.

        Args:
            image_id (str): ID of the image to get information for.

        Returns:
            dict: Image information, or None if failed.
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

        try:
            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                async with session.get(f'{self.api_url}/v1/Images/info/{image_id}', headers=headers) as response:
                    if response.status == 200:
                        return await response.json()  # Return the image info as JSON
                    else:
                        print(f"Failed to retrieve info for image with ID {image_id}: {response.status}")
                        return None
        except Exception as e:
            print(f"Error retrieving image info.\n -> {e}")
            return None

    async def ping_connection(self):
        try:
            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                async with session.get(f'{self.api_url}/v1/Images/ping',
                                       headers={'Authorization': f'Bearer {self.api_key}'}, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        print("API is reachable.")
                        return True
                    else:
                        print(f"API test failed with status {response.status}")
                        return False
        except Exception as e:
            print(f"Error testing connection.\n -> {e}")
            return False