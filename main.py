#!/usr/bin/env python3
"""
Copyright (C) Rodrigo Ferreira, All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
"""

"""
Main module for face detection and storage application.
Detects faces from webcam, shows them with green squares,
and saves unique faces to the faces directory.
"""

import cv2

from src.detector.face_detector import FaceDetector
from src.storage.face_storage import FaceStorage


def main():
    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    # Initialize face detector and storage
    detector = FaceDetector()
    storage = FaceStorage("faces")

    print("Starting face detection. Press 'q' to quit.")

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
                if storage.is_new_face(face_img):
                    filename = storage.save_face(face_img)
                    cv2.putText(display_frame, "Rosto Detectado!", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the frame with detected faces
        cv2.imshow('Detector de Rosto', display_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()