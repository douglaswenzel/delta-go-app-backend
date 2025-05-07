import cv2
import requests
import time

SERVER_URL = "http://127.0.0.1:8000"
REGISTER_MODE = False


def register_user():
    name = input("Nome completo: ")
    person_id = input("ID (matrícula/RG): ")

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    print("\nPosicione-se para a foto (aperte 's' para capturar)...")

    while True:
        ret, frame = cap.read()
        cv2.imshow('Cadastro', frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            _, img_encoded = cv2.imencode('.jpg', frame)
            break

    try:
        response = requests.post(
            f"{SERVER_URL}/register",
            data={"name": name, "person_id": person_id},
            files={"file": ("register.jpg", img_encoded.tobytes(), "image/jpeg")},
            timeout=10
        )
        print("\n✅" if response.status_code == 200 else "❌", response.json().get("detail", ""))

    except Exception as e:
        print(f"Erro: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()


def verify_access():
    cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
    print("\nPosicione-se para verificação...")

    ret, frame = cap.read()
    if not ret:
        print("Erro na câmera")
        return

    _, img_encoded = cv2.imencode('.jpg', frame)

    try:
        response = requests.post(
            f"{SERVER_URL}/verify",
            files={"file": ("verify.jpg", img_encoded.tobytes(), "image/jpeg")},
            timeout=10
        )
        data = response.json()

        if data.get("access"):
            user = data["user"]
            print(f"\n🎟️ Acesso LIBERADO para {user['name']} (ID: {user['person_id']})")
            # Acione aqui a catraca física
        else:
            print(f"\n⛔ Acesso NEGADO: {data.get('reason')}")

    except Exception as e:
        print(f"Erro: {str(e)}")
    finally:
        cap.release()


if __name__ == "__main__":
    print("\n=== Sistema de Controle de Acesso ===")

    if REGISTER_MODE:
        register_user()
    else:
        while True:
            input("Pressione ENTER para verificar (CTRL+C para sair)...")
            verify_access()