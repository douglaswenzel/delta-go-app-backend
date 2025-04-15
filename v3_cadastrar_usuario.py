import cv2
from modules.v3.face_registration import register_face


def cadastro_usuario():
    cap = cv2.VideoCapture(2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    user_id = int(input("Digite o ID do usuário para cadastro: "))

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow('Cadastro de Face', frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):  # Pressione 's' para salvar o rosto
            if register_face(user_id, frame):
                print("Cadastro concluído!")
                break

    cap.release()
    cv2.destroyAllWindows()


cadastro_usuario(3)
