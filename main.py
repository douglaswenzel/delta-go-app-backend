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
                user='dougl947_user',
                password=''
            )
            logging.info("Conexão com o MySQL estabelecida com sucesso")
        except Error as e:
            logging.error(f"Erro ao conectar ao MySQL: {e}")
            raise

    def register_user(self, user_data):
        try:
            cursor = self.connection.cursor()

            user_query = """
            INSERT INTO usuario (
                name, sobrenome, tipo, email, telefone, cpf, rg, nascimento,
                unidade, observacoes, permissao, endereco_rua, endereco_numero,
                endereco_complemento, endereco_bairro, endereco_cidade,
                endereco_estado, endereco_cep
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            user_values = (
                user_data['name'],
                user_data['sobrenome'],
                user_data['tipo'],
                user_data['email'],
                user_data['telefone'],
                user_data['cpf'],
                user_data['rg'],
                user_data['nascimento'],
                user_data['unidade'],
                user_data['observacoes'],
                user_data['permisso'],
                user_data['endereco']['rua'],
                user_data['endereco']['numero'],
                user_data['endereco']['complemento'],
                user_data['endereco']['bairro'],
                user_data['endereco']['cidade'],
                user_data['endereco']['estado'],
                user_data['endereco']['cep']
            )

            cursor.execute(user_query, user_values)
            user_id = cursor.lastrowid

            # Inserir dados específicos do tipo
            if user_data['tipo'] == 'funcionario':
                funcionario_query = """
                INSERT INTO funcionario (user_id, cargo, setor, data_admissao)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(funcionario_query, (
                    user_id,
                    user_data['funcionario']['cargo'],
                    user_data['funcionario']['setor'],
                    user_data['funcionario']['data_admissao']
                ))
            elif user_data['tipo'] == 'aluno':
                aluno_query = """
                INSERT INTO aluno (user_id, matricula, curso, turma, data_ingresso)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(aluno_query, (
                    user_id,
                    user_data['aluno']['matricula'],
                    user_data['aluno']['curso'],
                    user_data['aluno']['turma'],
                    user_data['aluno']['data_ingresso']
                ))
            else:
                visitante_query = """
                INSERT INTO visitante (user_id, motivo_visita, visitado, data_visita, empresa)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(visitante_query, (
                    user_id,
                    user_data['visitante']['motivo_visita'],
                    user_data['visitante']['visitado'],
                    user_data['visitante']['data_visita'],
                    user_data['visitante']['empresa']
                ))

            self.connection.commit()
            logging.info(f"Usuário {user_id} cadastrado com sucesso no banco de dados")
            return user_id

        except Error as e:
            self.connection.rollback()
            logging.error(f"Erro ao cadastrar usuário: {e}")
            raise
        finally:
            cursor.close()
