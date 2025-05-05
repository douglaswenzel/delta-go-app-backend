import mysql.connector
from datetime import datetime, timedelta
from modules.usersave import obter_nome_usuario


def registrar_log_acesso(user_id, acao, confidence, dispositivo="CATRACA 01"):
    try:
        conn = mysql.connector.connect(
            host='162.241.2.230',
            database='dougl947_DeltaGo',
            user='dougl947_user2',
            password='a#=d,F*No6)D'
        )
        cursor = conn.cursor()

        query = """
        INSERT INTO logs_acesso (usuario_id, acao, descricao, data_hora, ip_address, dispositivo)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        data_hora = datetime.now()
        descricao = f"Acesso {acao} com confiança de {confidence:.2f}%"
        ip_address = "192.168.0.10"

        valores = (user_id, acao, descricao, data_hora, ip_address, dispositivo)
        cursor.execute(query, valores)
        conn.commit()
        nome_usuario = obter_nome_usuario(user_id)

        print(f"Log registrado para usuário : {nome_usuario} com ID: {user_id} - {acao} - Confiança: {confidence:.2f}%")

    except mysql.connector.Error as err:
        print(f"Erro ao registrar log: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
