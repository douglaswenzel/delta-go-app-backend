import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging


class UserRegistration:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.logger = logging.getLogger('UserRegistration')

    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.logger.info("Conexão com o banco de dados estabelecida")
            return True
        except Error as e:
            self.logger.error(f"Erro ao conectar ao banco: {e}")
            return False

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

    def _register_employee(self, cursor, user_id, employee_data):
        """Registra dados específicos de funcionário"""
        query = """
        INSERT INTO funcionario (
            user_id, cargo, setor, data_admissao
        ) VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id,
            employee_data['cargo'],
            employee_data['setor'],
            employee_data['data_admissao']
        ))

    def _register_student(self, cursor, user_id, student_data):
        """Registra dados específicos de aluno"""
        query = """
        INSERT INTO aluno (
            usuario_id, matricula, curso, turma
        ) VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id,
            student_data['matricula'],
            student_data['curso'],
            student_data['turma']
        ))

    def _register_visitor(self, cursor, user_id, visitor_data):
        """Registra dados específicos de visitante"""
        query = """
        INSERT INTO visitante (
            usuario_id, motivo_visita, visitado, data_visita
        ) VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id,
            visitor_data['motivo_visita'],
            visitor_data['visitado'],
            visitor_data['data_visita']
        ))

    def register_user_photos(self, user_id, photo_paths):
        """Registra as fotos do usuário no banco de dados"""
        if not self.connect():
            raise ConnectionError("Não foi possível conectar ao banco de dados")

        cursor = None
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO fotos_usuarios (
                usuario_id, caminho_foto
            ) VALUES (%s, %s)
            """

            for path in photo_paths:
                cursor.execute(query, (user_id, path))

            self.connection.commit()
            self.logger.info(f"Fotos do usuário {user_id} registradas com sucesso")
            return True

        except Error as e:
            self.connection.rollback()
            self.logger.error(f"Erro ao registrar fotos: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()


# Exemplo de uso
if __name__ == "__main__":
    db_config = {
        'host': '162.241.2.230',
        'database': 'dougl947_DeltaGo',
        'user': 'dougl947_user2',
        'password': 'a#=d,F*No6)D'
    }

    user_data = {
        'name': 'Douglas',
        'sobrenome': 'Wenzel',
        'tipo': 'funcionario',
        'nascimento': '2002-03-15',
        'unidade': 'FATEC-VOTORANTIM',
        'observacoes': 'Desenvolvedor do sistema',
        'permissao': True,
        'funcionario': {
            'cargo': 'Analista de Sistemas',
            'setor': 'TI',
            'data_admissao': '2023-01-10'
        }
    }

    try:
        registration = UserRegistration(db_config)
        user_id = registration.register_user(user_data)

        # Após capturar as fotos (usando sua função cadastrar_usuario)
        photo_paths = [f'usuarios/{user_id}/001.jpg', f'usuarios/{user_id}/002.jpg']
        registration.register_user_photos(user_id, photo_paths)

        print(f"Usuário {user_id} registrado com sucesso!")
    except Exception as e:
        print(f"Erro ao registrar usuário: {e}")