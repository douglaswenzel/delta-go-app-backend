import cv2
import numpy as np
import time
from datetime import datetime

def controle_acesso():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=2, neighbors=16, grid_x=8, grid_y=8, threshold=85)
    recognizer.read('modelo_lbph.yml')

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    access_granted_time = None
    last_recognized_id = None
    cooldown_period = 5
    last_frame_time = 0
    frame_interval = 0.05

    while True:
        now = time.time()
        if now - last_frame_time < frame_interval:
            continue
        last_frame_time = now

        ret, frame = cap.read()
        if not ret:
            continue

        current_time = datetime.now()
        in_cooldown = access_granted_time and (current_time - access_granted_time).total_seconds() < cooldown_period

        if in_cooldown:
            border_width = 20
            frame[:border_width, :] = [0, 255, 0]
            frame[-border_width:, :] = [0, 255, 0]
            frame[:, :border_width] = [0, 255, 0]
            frame[:, -border_width:] = [0, 255, 0]

            text = f"Acesso autorizado para ID {last_recognized_id} | {confidence:.1f}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = frame.shape[0] - 30
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            remaining_time = cooldown_period - (current_time - access_granted_time).total_seconds()
            timer_text = f"Novo scan em: {remaining_time:.1f}s"
            cv2.putText(frame, timer_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow('Controle de Acesso', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:
            face_roi = gray_frame[y:y + h, x:x + w]
            face_resized = cv2.resize(face_roi, (100, 100))
            user_id, confidence = recognizer.predict(face_resized)

            if confidence < 95:
                access_granted_time = current_time
                last_recognized_id = user_id
                label = f"ID {user_id} ({confidence:.1f}%)"
                color = (0, 255, 0)
            else:
                label = "Não autorizado"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow('Controle de Acesso', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    controle_acesso()
