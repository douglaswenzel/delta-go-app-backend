import mysql.connector
from mysql.connector import Error
import cv2
import numpy as np
import os
from time import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='sistema_acesso.log'
)

class DatabaseManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='162.241.2.230',
                database='dougl947_DeltaGo',
                user='dougl947_user2',
                password='a#=d,F*No6)D'
            )
            logging.info("Conexão com o MySQL estabelecida com sucesso")
        except Error as e:
            logging.error(f"Erro ao conectar ao MySQL: {e}")
            raise

    def validate_user_data(self, user_data):
        """Valida os dados do usuário antes do registro"""
        required_fields = {
            'base': ['name', 'sobrenome', 'tipo', 'nascimento', 'unidade', 'permissao'],
            'funcionario': ['cargo', 'setor', 'data_admissao'],
            'aluno': ['matricula', 'curso', 'turma'],
            'visitante': ['motivo_visita', 'visitado', 'data_visita']
        }

        # Verifica campos básicos
        for field in required_fields['base']:
            if field not in user_data or user_data[field] in (None, ''):
                raise ValueError(f"Campo obrigatório faltando: {field}")

        # Verifica campos específicos do tipo
        user_type = user_data['tipo']
        if user_type not in ['funcionario', 'aluno', 'visitante']:
            raise ValueError("Tipo de usuário inválido")

        for field in required_fields[user_type]:
            if field not in user_data[user_type] or user_data[user_type][field] in (None, ''):
                raise ValueError(f"Campo obrigatório faltando para {user_type}: {field}")

        return True

    def register_user(self, user_data):
        """Registra um novo usuário no sistema"""
        if not self.connect():
            raise ConnectionError("Não foi possível conectar ao banco de dados")

        cursor = None
        try:
            self.validate_user_data(user_data)
            cursor = self.connection.cursor()

            # 1. Registrar dados básicos do usuário
            user_query = """
            INSERT INTO usuario (
                name, sobrenome, tipo, nascimento, unidade, 
                observacoes, permissao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            user_values = (
                user_data['name'],
                user_data['sobrenome'],
                user_data['tipo'],
                user_data['nascimento'],
                user_data['unidade'],
                user_data.get('observacoes', ''),
                int(user_data['permissao'])
            )

            cursor.execute(user_query, user_values)
            user_id = cursor.lastrowid

            # 2. Registrar dados específicos do tipo
            if user_data['tipo'] == 'funcionario':
                self._register_employee(cursor, user_id, user_data['funcionario'])
            elif user_data['tipo'] == 'aluno':
                self._register_student(cursor, user_id, user_data['aluno'])
            else:
                self._register_visitor(cursor, user_id, user_data['visitante'])

            self.connection.commit()
            self.logger.info(f"Usuário {user_id} registrado com sucesso")
            return user_id

        except Error as e:
            self.connection.rollback()
            self.logger.error(f"Erro no banco de dados: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Erro de validação: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
    def register_photos(self, user_id, photo_paths):
        try:
            cursor = self.connection.cursor()
            photo_query = """
            INSERT INTO fotos_usuarios (usuario_id, caminho_foto)
            VALUES (%s, %s)
            """

            for path in photo_paths:
                cursor.execute(photo_query, (user_id, path))

            self.connection.commit()
            logging.info(f"Fotos do usuário {user_id} registradas com sucesso")
        except Error as e:
            self.connection.rollback()
            logging.error(f"Erro ao registrar fotos: {e}")
            raise
        finally:
            cursor.close()

    def log_access(self, user_id=None, acao="", descricao="", ip_address="", dispositivo=""):
        try:
            cursor = self.connection.cursor()
            log_query = """
            INSERT INTO logs_acesso (usuario_id, acao, descricao, ip_address, dispositivo)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(log_query, (user_id, acao, descricao, ip_address, dispositivo))
            self.connection.commit()
        except Error as e:
            logging.error(f"Erro ao registrar log: {e}")
        finally:
            cursor.close()

    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            logging.info("Conexão com MySQL encerrada")

def coletar_dados_usuario():
    """Coleta dados do usuário via terminal"""
    print("\n--- Cadastro de Usuário ---")

    user_data = {
        "name": input("Nome: "),
        "sobrenome": input("Sobrenome: "),
        "tipo": None,
        "nascimento": input("Data de Nascimento (YYYY-MM-DD): "),
        "unidade": input("Unidade: "),
        "observacoes": input("Observações: "),
        "permisso": input("Tem permissão? (s/n): ").lower() == 's'
    }
    tipo = ""
    while tipo not in ['funcionario', 'aluno', 'visitante']:
        tipo = input("Tipo (funcionario/aluno/visitante): ").lower()

    user_data["tipo"] = tipo

    if tipo == "funcionario":
        user_data["funcionario"] = {
            "cargo": input("Cargo: "),
            "setor": input("Setor: "),
            "data_admissao": input("Data de Admissão (YYYY-MM-DD): ")
        }
    elif tipo == "aluno":
        user_data["aluno"] = {
            "matricula": input("Matrícula: "),
            "curso": input("Curso: "),
            "turma": input("Turma: "),
            "data_ingresso": input("Data de Ingresso (YYYY-MM-DD): ")
        }
    else:
        user_data["visitante"] = {
            "motivo_visita": input("Motivo da Visita: "),
            "visitado": input("Visitado: "),
            "data_visita": input("Data da Visita (YYYY-MM-DD HH:MM): "),
            "empresa": input("Empresa: ")
        }

    return user_data


def cadastrar_usuario_completo():
    db = DatabaseManager()

    try:
        # 1. Registrar log de início do cadastro
        db.log_access(acao="INICIO_CADASTRO", descricao="Início do processo de cadastro")

        # 2. Coletar dados do usuário
        user_data = coletar_dados_usuario()

        # 3. Registrar no banco de dados
        user_id = db.register_user(user_data)
        db.log_access(user_id, "CADASTRO_DADOS", "Dados pessoais cadastrados")

        # 4. Capturar imagens faciais
        print("\nAgora vamos capturar as imagens para reconhecimento facial...")
        photo_paths = cadastrar_usuario(user_id)

        # 5. Registrar caminhos das fotos no banco
        db.register_photos(user_id, photo_paths)
        db.log_access(user_id, "CADASTRO_FOTOS", f"{len(photo_paths)} fotos cadastradas")

        print("\nCadastro completo realizado com sucesso!")
        db.log_access(user_id, "CADASTRO_CONCLUIDO", "Processo de cadastro concluído")

    except Exception as e:
        logging.error(f"Falha no cadastro: {e}")
        db.log_access(acao="ERRO_CADASTRO", descricao=f"Erro durante cadastro: {str(e)}")
        print("Ocorreu um erro durante o cadastro. Por favor, tente novamente.")
    finally:
        del db


if __name__ == "__main__":
    cadastrar_usuario_completo()