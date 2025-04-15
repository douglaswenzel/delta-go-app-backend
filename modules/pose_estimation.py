import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1,
                                   refine_landmarks=True, min_detection_confidence=0.5)

def estimate_head_orientation(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)

    if not results.multi_face_landmarks:
        return None

    landmarks = results.multi_face_landmarks[0].landmark
    left_eye = np.array([landmarks[33].x, landmarks[33].y])
    right_eye = np.array([landmarks[263].x, landmarks[263].y])
    nose_tip = np.array([landmarks[1].x, landmarks[1].y])
    chin = np.array([landmarks[152].x, landmarks[152].y])

    eye_delta_x = right_eye[0] - left_eye[0]
    eye_delta_y = right_eye[1] - left_eye[1]

    angle_yaw = np.arctan2(eye_delta_y, eye_delta_x) * 180 / np.pi
    angle_pitch = (nose_tip[1] - chin[1]) * 100

    return angle_yaw, angle_pitch

def sugestao_pose(angle_yaw, angle_pitch):
    if angle_yaw < -10:
        return "VIRE UM POUCO À DIREITA"
    elif angle_yaw > 10:
        return "VIRE UM POUCO À ESQUERDA"
    elif angle_pitch < -3:
        return "LEVANTE LEVEMENTE O ROSTO"
    elif angle_pitch > 3:
        return "ABAIXE UM POUCO O ROSTO"
    else:
        return "MANTENHA A POSIÇÃO"
