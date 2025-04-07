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