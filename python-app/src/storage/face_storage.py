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

from src.utils.config import SIMILARITY_THRESHOLD, USE_SAVED_IMAGES, DEBUG_MODE


class FaceStorage:
    def __init__(self, web_request):
        """
        Initialize the face storage system using a REST API.

        Args:
            web_request (WebRequest): WebRequest class for making API calls
        """
        self.stored_faces = None
        self.web_request = web_request

        self.debug_mode = DEBUG_MODE
        self.similarity_threshold = SIMILARITY_THRESHOLD # Lower value = more strict comparison
        self.debug_mode = DEBUG_MODE
        self.use_saved_images = USE_SAVED_IMAGES

    async def load_stored_faces(self):
        self.stored_faces = await self._get_stored_faces_by_request()

    async def _get_stored_faces_by_request(self):
        """
        Optionally load existing face data from the API.

        Returns:
            list: List of (image_id, grayscale_face_image) tuples
        """

        # TODO: Implement loading stored faces from the API
        # 64 is the colour mode for grayscale images
        return await self.web_request.get_all_images(colour_mode_id=cv2.COLOR_BGR2GRAY) or []

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

        if len(self.stored_faces) == 0:
            return True

        resized = cv2.resize(face_img, (100, 100))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        if self.debug_mode:
            print("[DEBUG] Face image shape:", face_img.shape)
            print("[DEBUG] Stored faces:", len(self.stored_faces))

        similarities = []
        is_similar = False

        for stored_data in self.stored_faces:
            stored_gray = stored_data[1]
            result = cv2.matchTemplate(gray, stored_gray, cv2.TM_CCOEFF_NORMED)
            similarity = np.max(result)
            similarities.append(similarity)

            if similarity > self.similarity_threshold:
                is_similar = True

        if self.debug_mode:
            formatted = ", ".join(f"{s:.2f}".rstrip('0').rstrip('.') for s in similarities)
            print(f"[DEBUG] Similarities:\n -> {formatted}")

        if is_similar:
            return False

        print("Face is new!")
        return True

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
            image_id = await self.web_request.upload_image(face_img)

            if not image_id:
                print("Failed to upload image to API.")
                return None

            # Convert face image to grayscale for storing locally
            resized = cv2.resize(face_img, (100, 100))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

            # Save the face image and ID in stored_faces for future comparison
            self.stored_faces.append((image_id, gray))

            if self.debug_mode:
                print(f"[DEBUG] Image uploaded successfully with ID: {image_id}")

        except Exception as e:
            print(f"Error uploading image to API: {e}")
            return None