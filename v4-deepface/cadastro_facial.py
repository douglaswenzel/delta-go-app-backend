import cv2
import os
import time
import json
import mysql.connector
from deepface import DeepFace

DB_CONFIG = {
    'host': '162.241.2.230',
    'port': '3306',
    'user': 'dougl947_user',
    'database': 'dougl947_DeltaGo'
}
OUTPUT_DIR = "C:\\facial_recognition\\usuarios"


def conectar_banco():
    return mysql.connector.connect(**DB_CONFIG)


def cadastrar_usuario():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW para melhor performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    nome = input("Digite o nome do usuário: ")
    matricula = input("Digite a matrícula: ")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, registration_number) VALUES (%s, %s)",
        (nome, matricula)
    )
    user_id = cursor.lastrowid
    conn.commit()

    count = 0
    required_poses = ['center', 'left', 'right', 'up', 'down']

    print("\nPosicione o rosto conforme as instruções...")

    while count < 15:  # 3 imagens por pose
        ret, frame = cap.read()
        if not ret:
            continue

        try:
            faces = DeepFace.extract_faces(frame, detector_backend='opencv')
            if len(faces) == 1:
                face = faces[0]
                x, y, w, h = face['facial_area'].values()
                face_img = frame[y:y + h, x:x + w]

                embedding = DeepFace.represent(face_img, model_name='ArcFace')

                cursor.execute(
                    "INSERT INTO face_embeddings (user_id, embedding_json) VALUES (%s, %s)",
                    (user_id, json.dumps(embedding))  # Adicione o parêntese faltante
                )
                conn.commit()

                pose = required_poses[count % len(required_poses)]
                timestamp = int(time.time())
                img_path = os.path.join(OUTPUT_DIR, f"{user_id}_{pose}_{timestamp}.jpg")
                cv2.imwrite(img_path, face_img)

                count += 1
                print(f"Captura {count}/15 concluída - Pose: {pose}")

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Capturas: {count}/15", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        except Exception as e:
            print(f"Erro: {str(e)}")

        cv2.imshow('Cadastro Facial', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    cursor.close()
    conn.close()
    print(f"\nUsuário {nome} cadastrado com sucesso! ID: {user_id}")


if __name__ == "__main__":
    cadastrar_usuario()