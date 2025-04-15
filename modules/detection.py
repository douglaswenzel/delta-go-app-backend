import cv2

face_cascade = cv2.CascadeClassifier('Cascade/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('Cascade/haarcascade_eye.xml')

def detect_faces(processed_frame):
    return face_cascade.detectMultiScale(
        processed_frame,
        scaleFactor=1.05,
        minNeighbors=6,
        minSize=(100, 100),
        flags=cv2.CASCADE_FIND_BIGGEST_OBJECT
    )

def detect_eyes(face_roi):
    return eye_cascade.detectMultiScale(
        face_roi,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
