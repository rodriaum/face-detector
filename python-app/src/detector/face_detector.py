#!/usr/bin/env python3
"""
Copyright (C) Rodrigo Ferreira, All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Face detector module using OpenCV's Haar Cascade classifier.
"""

import cv2

from src.utils.config import CASCADE_CLASSIFIER, CASCADE_SCALE_FACTOR, CASCADE_MIN_NEIGHBORS, CASCADE_MIN_SIZE


class FaceDetector:
    def __init__(self, cascade_path=None):
        """
        Initialize the face detector.

        Args:
            cascade_path (str, optional): Path to the Haar Cascade XML file.
                If None, the default OpenCV file will be used.
        """
        if cascade_path is None:
            # Use OpenCV's built-in face cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + CASCADE_CLASSIFIER)
        else:
            self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            raise ValueError("Error loading face cascade classifier")

    def detect_faces(self, image, scale_factor=CASCADE_SCALE_FACTOR, min_neighbors=CASCADE_MIN_NEIGHBORS, min_size=CASCADE_MIN_SIZE):
        """
        Detect faces in the input image.

        Args:
            image: Input image (numpy array)
            scale_factor (float): Parameter specifying how much the image size is reduced at each scale
            min_neighbors (int): Parameter specifying how many neighbors each candidate rectangle should have
            min_size (tuple): Minimum possible object size. Objects smaller than this are ignored

        Returns:
            list: List of (x, y, w, h) tuples for each detected face
        """
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size
        )

        return faces