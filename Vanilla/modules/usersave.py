import mysql.connector
import glob
import os
from datetime import datetime

def obter_nome_usuario(user_id):
    try:
        conn = mysql.connector.connect(
            host='162.241.2.230',
            database='dougl947_DeltaGo',
            user='dougl947_user2',
            password='a#=d,F*No6)D'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT name, sobrenome FROM usuario WHERE user_id = %s", (user_id,))
        resultado = cursor.fetchone()
        if resultado:
            return f"{resultado[0]} {resultado[1]}"
        else:
            return "Usuário desconhecido"
    except mysql.connector.Error as err:
        print(f"Erro ao obter nome: {err}")
        return "Erro na consulta"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
