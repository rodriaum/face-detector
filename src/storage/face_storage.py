#!/usr/bin/env python3
"""
Copyright (C) Rodrigo Ferreira, All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Face storage module for saving and comparing face images.
"""

import cv2
import numpy as np
from aiohttp import FormData

from src.utils.config import SIMILARITY_THRESHOLD, DEBUG_MODE, USE_SAVED_IMAGES


class FaceStorage:
    def __init__(self, web_request):
        """
        Initialize the face storage system using a REST API.

        Args:
            web_request (WebRequest): WebRequest class for making API calls
        """
        self.web_request = web_request
        self.stored_faces = self._load_stored_faces()

        self.similarity_threshold = SIMILARITY_THRESHOLD # Lower value = more strict comparison
        self.debug_mode = DEBUG_MODE
        self.use_saved_images = USE_SAVED_IMAGES

    async def _load_stored_faces(self):
        """
        Optionally load existing face data from the API.

        Returns:
            list: List of (image_id, grayscale_face_image) tuples
        """

        # TODO: Implement loading stored faces from the API
        # 64 is the colour mode for grayscale images
        return await self.web_request.get_all_images(colour_mode_id=6) or []

    async def is_new_face(self, face_img):
        """
        Check if a face is new (not similar to any stored face).

        Args:
            face_img: Face image (NumPy array)

        Returns:
            bool: True if the face is new, False if it's similar to a stored one
        """
        if not self.use_saved_images:
            return True

        stored_faces = await self.stored_faces

        if len(stored_faces) == 0:
            return True

        resized = cv2.resize(face_img, (100, 100))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        for _, stored_gray in stored_faces:
            result = cv2.matchTemplate(gray, stored_gray, cv2.TM_CCOEFF_NORMED)
            similarity = np.max(result)

            if similarity > self.similarity_threshold:
                return False  # Similar face found

        return True  # No match found

    async def save_face(self, face_img):
        """
        Asynchronously upload a face image to the API and keep it in memory for future comparisons.

        Args:
            face_img: Face image (NumPy array)

        Returns:
            str or None: Image ID returned by the API, or None if failed
        """
        # Encode image to JPEG format
        success, img_encoded = cv2.imencode('.jpg', face_img)
        if not success:
            print("Failed to encode image.")
            return None

        # Create the multipart form data to send the image
        form = FormData()
        form.add_field('file', img_encoded.tobytes(), content_type='image/jpeg', filename='face.jpg')

        try:
            await self.web_request.upload_image(face_img)
        except Exception as e:
            print(f"Error uploading image to API: {e}")
            return None