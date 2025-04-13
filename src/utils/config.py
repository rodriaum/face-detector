"""
Copyright (C) Rodrigo Ferreira, All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

System constants and settings
"""

SIMILARITY_THRESHOLD = 0.7 # Lower value = more strict comparison
CLIENT_TIMEOUT = 30
SAVE_FACE_TIMEOUT = 5

DEBUG_MODE = True
USE_SAVED_IMAGES = True # If True, can have issues in performance

CASCADE_CLASSIFIER = "haarcascade_frontalface_default.xml"
CASCADE_SCALE_FACTOR = 1.1
CASCADE_MIN_NEIGHBORS = 5
CASCADE_MIN_SIZE = (30, 30)

WINDOW_NAME = "Detector de Rosto"
BOX_TEXT = "Rosto Detectado"