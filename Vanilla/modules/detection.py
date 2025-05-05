import cv2
import os

FACE_CASCADE_PATH = 'Cascade/haarcascade_frontalface_default.xml'
EYE_CASCADE_PATH = 'Cascade/haarcascade_eye.xml'

if not os.path.exists(FACE_CASCADE_PATH) or not os.path.exists(EYE_CASCADE_PATH):
    raise FileNotFoundError("Arquivos de cascade XML não encontrados na pasta 'Cascade/'.")

face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)

def detect_faces(processed_frame):
    faces = face_cascade.detectMultiScale(
        processed_frame,
        scaleFactor=1.05,
        minNeighbors=6,
        minSize=(100, 100),
        flags=cv2.CASCADE_FIND_BIGGEST_OBJECT
    )
    return faces

def detect_eyes(face_roi):
    eyes = eye_cascade.detectMultiScale(
        face_roi,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    return eyes