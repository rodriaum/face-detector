"""
Copyright (C) Rodrigo Ferreira, All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
"""
import base64
import ssl

import aiohttp
import cv2
import numpy as np
from aiohttp import FormData, ClientTimeout

from src.utils.config import CLIENT_TIMEOUT


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

        self.client_timeout = ClientTimeout(total=CLIENT_TIMEOUT)

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

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

        # Send the POST request to upload the image
        response = await self._send_post_request('v1/Images/upload', form, self.headers)

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
        try:
            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                async with session.delete(f'{self.api_url}/v1/images/{image_id}', headers=self.headers, ssl=self.ssl_context) as response:
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
        try:
            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                async with session.get(f'{self.api_url}/v1/images/info/{image_id}', headers=self.headers, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        return await response.json()  # Return the image info as JSON
                    else:
                        print(f"Failed to retrieve info for image with ID {image_id}: {response.status}")
                        return None
        except Exception as e:
            print(f"Error retrieving image info.\n -> {e}")
            return None

    async def get_all_images(self, colour_mode_id=None):
        """
        Retrieves all stored images from the API and converts them to grayscale.

        Args:
            colour_mode_id (int): ID of the colour mode to use for conversion.

        Returns:
            list: List of (image_id, grayscale_face_image) tuples.
        """
        try:
            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                async with session.get(f'{self.api_url}/v1/images/get', headers=self.headers, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []

                        for item in data:
                            image_id = item.get("id")
                            base64_str = item.get("base64")

                            if not base64_str:
                                continue

                            # Decode base64 to image
                            image_data = base64.b64decode(base64_str)
                            np_arr = np.frombuffer(image_data, np.uint8)
                            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                            if img is None:
                                continue

                            if colour_mode_id is not None:
                                gray_img = cv2.cvtColor(img, colour_mode_id)

                            results.append((image_id, gray_img))

                        return results

                    else:
                        print(f"Failed to fetch images: status {response.status}")
                        return []
        except Exception as e:
            print(f"Error while fetching images.\n -> {e}")
            return []

    async def ping_connection(self):
        try:
            async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
                async with session.get(f'{self.api_url}/v1/images/ping',
                                       headers=self.headers, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        print("API is reachable.")
                        return True
                    else:
                        print(f"API test failed with status {response.status}")
                        return False
        except Exception as e:
            print(f"Error testing connection.\n -> {e}")
            return False