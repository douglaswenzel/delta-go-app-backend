import cv2
import os
from time import time
from config import *
from modules.preprocessing import apply_adaptive_preprocessing, calculate_sharpness, check_lighting
from modules.detection import detect_faces, detect_eyes
from modules.pose_estimation import estimate_head_orientation, sugestao_pose
from modules.validation import validate_eyes
from modules.face_capture import capture_face_variations
from modules.usersave import obter_nome_usuario


def cadastrar_usuario(user_id):
    cap = cv2.VideoCapture(2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    output_dir = f'usuarios/{user_id:03d}'
    os.makedirs(output_dir, exist_ok=True)

    count = 0
    last_capture = 0
    required_poses = ['center', 'left', 'right', 'up', 'down']
    current_pose_index = 0

    while count < TOTAL_SAMPLES:
        ret, frame = cap.read()
        if not ret:
            continue

        processed = apply_adaptive_preprocessing(frame)
        faces = detect_faces(processed)

        frame_has_face = False
        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            face_roi = processed[y:y + h, x:x + w]
            eyes = detect_eyes(face_roi)

            current_time = time()

            if (validate_eyes(eyes) and
                    calculate_sharpness(face_roi) > MIN_SHARPNESS and
                    check_lighting(face_roi) and
                    (current_time - last_capture) > CAPTURE_DELAY):

                count = capture_face_variations(face_roi, output_dir, count, required_poses[current_pose_index])
                last_capture = current_time
                print(f"Captura {count} - Pose: {required_poses[current_pose_index]}")

                if count % (len(required_poses) * 3) == 0:
                    current_pose_index = (current_pose_index + 1) % len(required_poses)
                    print(f"\nMude para a pose: {required_poses[current_pose_index].upper()}\n")

                frame_has_face = True

        orientation = estimate_head_orientation(frame)
        if orientation:
            yaw, pitch = orientation
            instrucoes = sugestao_pose(yaw, pitch)
        else:
            instrucoes = "Centralize o rosto visivelmente"

        color = (0, 255, 0) if frame_has_face else (0, 0, 255)
        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        cv2.putText(frame, instrucoes, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"Capturas: {count}/{TOTAL_SAMPLES}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0),
                    2)
        cv2.imshow('Cadastro Facial Inteligente', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Cadastro concluído com sucesso!")


if __name__ == "__main__":
    cadastrar_usuario()