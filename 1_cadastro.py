import cv2
import numpy as np
import os
from time import time

MIN_SHARPNESS = 80
MIN_EYE_SIZE_RATIO = 1.3
MIN_EYE_AREA = 900
CAPTURE_DELAY = 1.5
TOTAL_SAMPLES = 35
RESIZED_DIM = (200, 200)

def check_lighting(face_roi):
    avg_brightness = np.mean(face_roi)
    return 70 <= avg_brightness <= 200

def calculate_sharpness(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def apply_adaptive_preprocessing(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    normalized = clahe.apply(gray)
    denoised = cv2.fastNlMeansDenoising(normalized, h=15)
    return denoised


def validate_eyes(eye_regions):
    if len(eye_regions) < 2:
        return False

    eye_areas = [w * h for (x, y, w, h) in eye_regions]
    if any(area < MIN_EYE_AREA for area in eye_areas):
        return False

    size_ratio = max(eye_areas) / min(eye_areas)
    return size_ratio <= MIN_EYE_SIZE_RATIO

def capture_face_variations(face_roi, output_path, count, pose):
    for angle in [-10, 0, 10]:
        M = cv2.getRotationMatrix2D((face_roi.shape[1]/2, face_roi.shape[0]/2), angle, 1)
        rotated = cv2.warpAffine(face_roi, M, (face_roi.shape[1], face_roi.shape[0]))
        resized = cv2.resize(rotated, RESIZED_DIM)
        cv2.imwrite(f'{output_path}/{count:03d}_{pose}.jpg', resized)
        count += 1
    return count


def cadastrar_usuario(user_id):
    cap = cv2.VideoCapture(2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    output_dir = f'usuarios/{user_id:03d}'
    os.makedirs(output_dir, exist_ok=True)

    face_cascade = cv2.CascadeClassifier('Cascade/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('Cascade/haarcascade_eye.xml')

    count = 0
    last_capture = 0
    required_poses = ['center', 'left', 'right', 'up', 'down']
    current_pose_index = 0

    # Variáveis de inicialização
    x, y, w, h = 0, 0, 0, 0

    while count < TOTAL_SAMPLES:
        ret, frame = cap.read()
        if not ret: continue

        processed = apply_adaptive_preprocessing(frame)
        faces = face_cascade.detectMultiScale(
            processed,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(100, 100),
            flags=cv2.CASCADE_FIND_BIGGEST_OBJECT
        )

        frame_has_face = False
        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            face_roi = processed[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(
                face_roi,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            current_time = time()

            if (validate_eyes(eyes) and
                    calculate_sharpness(face_roi) > MIN_SHARPNESS and
                    check_lighting(face_roi) and
                    (current_time - last_capture) > CAPTURE_DELAY):

                count = capture_face_variations(
                    face_roi,
                    output_dir,
                    count,
                    required_poses[current_pose_index]
                )

                last_capture = current_time
                print(f"Captura {count} - Pose: {required_poses[current_pose_index]}")

                if count % (len(required_poses) * 3) == 0:
                    current_pose_index = (current_pose_index + 1) % len(required_poses)
                    print(f"\nMude para a pose: {required_poses[current_pose_index].upper()}\n")

                frame_has_face = True

        # Feedback visual
        if frame_has_face:
            color = (0, 255, 0)
            text = f"POSE: {required_poses[current_pose_index].upper()}"
        else:
            color = (0, 0, 255)
            text = "Centralize o rosto na area indicada"

        if len(faces) == 1:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Capturas: {count}/35", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.imshow('Registro Facial - Siga as Instrucoes', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Cadastro concluído com sucesso!")

cadastrar_usuario(1)
