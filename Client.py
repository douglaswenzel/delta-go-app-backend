import cv2
import requests

# Configurações CORRETAS (ajuste conforme sua rede)
SERVER_IP = "192.168.1.136"  # Substitua pelo IP real do seu servidor
SERVER_PORT = "8000"
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}/verify"  # URL completa


def capture_and_verify():
    cap = cv2.VideoCapture(0)
    try:
        ret, frame = cap.read()
        if not ret:
            print("Erro: Falha na captura da câmera")
            return

        # Otimização para hardware limitado
        frame = cv2.resize(frame, (320, 240))
        _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])

        try:
            response = requests.post(
                SERVER_URL,
                files={'file': ('face.jpg', img_encoded.tobytes(), 'image/jpeg')},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                print("Resposta do servidor:", data)
            else:
                print(f"Erro no servidor (HTTP {response.status_code}): {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Falha na comunicação com o servidor: {str(e)}")
            print(f"Verifique se o servidor está rodando em {SERVER_URL}")
            print("Confira:")
            print("- IP do servidor está correto?")
            print("- Servidor e cliente estão na mesma rede?")
            print("- Firewall permite conexões na porta 8000?")

    finally:
        cap.release()


if __name__ == "__main__":
    print("Sistema de Controle de Acesso Iniciado")
    print(f"Conectando ao servidor em: {SERVER_URL}")

    while True:
        input("Pressione ENTER para capturar...")
        capture_and_verify()