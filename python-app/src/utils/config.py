"""
Copyright (C) Rodrigo Ferreira, All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

System constants and settings
"""

from screeninfo import get_monitors

APP_IDENTIFIER = "fd-app-instance-01"

SIMILARITY_THRESHOLD = 0.6 # Lower value = more strict comparison
CLIENT_TIMEOUT = 30
SAVE_FACE_TIMEOUT = 5

DEBUG_MODE = True
USE_SAVED_IMAGES = True # If True, can have issues in performance

CASCADE_CLASSIFIER = "haarcascade_frontalface_default.xml"
CASCADE_SCALE_FACTOR = 1.1
CASCADE_MIN_NEIGHBORS = 5
CASCADE_MIN_SIZE = (30, 30)

FIRST_MONITOR = get_monitors()[0]
WINDOW_SIZE = (FIRST_MONITOR.width, FIRST_MONITOR.height)

WINDOW_NAME = "Detector de Rosto"
BOX_TEXT = "Rosto Detectado"