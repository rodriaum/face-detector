#!/usr/bin/env python3
"""
Copyright (C) Rodrigo Ferreira, All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Main module for face detection and storage application.
Detects faces from webcam, shows them with green squares,
and saves unique faces to the faces directory.
"""

import asyncio
import os
import time

import cv2
from dotenv import load_dotenv

from src.detector.face_detector import FaceDetector
from src.request.web_request import WebRequest
from src.storage.face_storage import FaceStorage
from src.utils.config import WINDOW_NAME, BOX_TEXT, SAVE_FACE_TIMEOUT, WINDOW_SIZE


async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    (w, h) = WINDOW_SIZE
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, h)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    api_url = os.getenv("FACE_STORAGE_API_URL")
    api_key = os.getenv("FACE_STORAGE_API_KEY")

    if not api_url or not api_key:
        print("API URL or API key not found in .env file.")
        return

    # Initialize modules
    web_request = WebRequest(api_url, api_key)

    # Check if the connection to the API is successful
    if not await web_request.ping_connection():
        return

    detector = FaceDetector()
    storage = FaceStorage(web_request)

    await storage.load_stored_faces()

    print("Starting face detection. Press 'q' to quit.")

    last_save_time = int(time.time())

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Create a copy of the frame for drawing
        display_frame = frame.copy()

        # Detect faces in the frame
        faces = detector.detect_faces(frame)

        # Process each detected face
        for (x, y, w, h) in faces:
            # Draw a green square around the face
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Extract the face region
            face_img = frame[y:y + h, x:x + w]

            # Try to save the face if it's new
            if face_img.size > 0:  # Make sure face region is valid
                current_time = int(time.time())

                if current_time - last_save_time >= SAVE_FACE_TIMEOUT:
                    if await storage.is_new_face(face_img):

                        await storage.save_face(face_img)
                        last_save_time = current_time

                        cv2.putText(display_frame, BOX_TEXT, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        print("[DEBUG] New face detected and saved.")
                    else:
                        print("[DEBUG] Face already exists in storage.")

        # Display the frame with detected faces
        cv2.imshow(WINDOW_NAME, display_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    asyncio.run(main())