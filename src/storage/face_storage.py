#!/usr/bin/env python3
"""
Copyright (C) Rodrigo Ferreira, All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
"""

"""
Face storage module for saving and comparing face images.
"""

import os
import time
import uuid

import cv2
import numpy as np


class FaceStorage:
    def __init__(self, storage_dir):
        """
        Initialize the face storage system.

        Args:
            storage_dir (str): Directory to store face images
        """
        self.storage_dir = storage_dir

        # Create the storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        # Load existing faces for comparison
        self.stored_faces = self._load_stored_faces()

        # Parameters for face comparison
        self.similarity_threshold = 0.7  # Lower values require more similarity

    def _load_stored_faces(self):
        """
        Load all stored face images for comparison.

        Returns:
            list: List of (filename, image) tuples for all stored faces
        """
        stored_faces = []

        for filename in os.listdir(self.storage_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    image = cv2.imread(filepath)
                    if image is not None:
                        # Resize for consistent comparison
                        image = cv2.resize(image, (100, 100))
                        stored_faces.append((filename, image))
                except Exception as e:
                    print(f"Error loading image {filename}: {e}")

        return stored_faces

    def is_new_face(self, face_img):
        """
        Check if a face is new (not similar to any stored face).

        Args:
            face_img: Face image to check

        Returns:
            bool: True if this is a new face, False if similar to existing face
        """
        if len(self.stored_faces) == 0:
            return True

        # Resize for consistent comparison
        if face_img.shape[0] > 0 and face_img.shape[1] > 0:
            face_resized = cv2.resize(face_img, (100, 100))

            # Convert to grayscale for better comparison
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)

            # Check similarity with each stored face
            for _, stored_face in self.stored_faces:
                stored_gray = cv2.cvtColor(stored_face, cv2.COLOR_BGR2GRAY)

                # Calculate normalized correlation coefficient
                result = cv2.matchTemplate(face_gray, stored_gray, cv2.TM_CCOEFF_NORMED)
                similarity = np.max(result)

                if similarity > self.similarity_threshold:
                    return False  # Similar face found

        return True  # No similar face found

    def save_face(self, face_img):
        """
        Save a face image to storage.

        Args:
            face_img: Face image to save

        Returns:
            str: Filename of the saved image
        """
        # Generate a unique filename using UUID and timestamp
        filename = f"face_{uuid.uuid4().hex}_{int(time.time())}.jpg"
        filepath = os.path.join(self.storage_dir, filename)

        # Save the image
        cv2.imwrite(filepath, face_img)

        # Add to stored faces for future comparison
        if face_img.shape[0] > 0 and face_img.shape[1] > 0:
            resized_face = cv2.resize(face_img, (100, 100))
            self.stored_faces.append((filename, resized_face))

        return filename