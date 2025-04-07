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