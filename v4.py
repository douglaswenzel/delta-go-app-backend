import cv2
import requests
import time

SERVER_URL = "http://127.0.0.1:8000"
REGISTER_MODE = False

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def register_user():
    name = input("Nome completo: ")
    person_id = input("ID (matrícula/RG): ")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("\nAguardando detecção de rosto para cadastro...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro na câmera")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            print("📸 Rosto detectado. Enviando para cadastro...")

            _, img_encoded = cv2.imencode('.jpg', frame)
            try:
                response = requests.post(
                    f"{SERVER_URL}/register",
                    data={"name": name, "person_id": person_id},
                    files={"file": ("register.jpg", img_encoded.tobytes(), "image/jpeg")},
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ Cadastro realizado com sucesso!")
                else:
                    print("❌ Falha no cadastro:", response.json().get("detail", "Erro desconhecido"))
                time.sleep(2)
                break

            except Exception as e:
                print(f"Erro: {str(e)}")
                break

        cv2.imshow("Cadastro de Usuário", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Cadastro cancelado pelo usuário.")
            break

    cap.release()
    cv2.destroyAllWindows()

def verify_access():
    cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
    print("\nAguardando detecção de rosto...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro na câmera")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            print("🔍 Rosto detectado. Enviando para verificação...")

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
                    print(f"\n✅ Acesso LIBERADO para {user['name']} (ID: {user['person_id']})")
                else:
                    print(f"\n⛔ Acesso NEGADO: {data.get('reason', 'Usuário não reconhecido')}")

                time.sleep(3)

            except Exception as e:
                print(f"Erro: {str(e)}")

        cv2.imshow("Verificação de Acesso", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("\n=== Sistema de Controle de Acesso ===")

    if REGISTER_MODE:
        register_user()
    else:
        verify_access()
