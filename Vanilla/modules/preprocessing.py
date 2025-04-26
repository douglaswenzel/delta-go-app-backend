import cv2
import numpy as np

def apply_adaptive_preprocessing(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    normalized = clahe.apply(gray)
    denoised = cv2.fastNlMeansDenoising(normalized, h=15)
    return denoised

def calculate_sharpness(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def check_lighting(image):
    avg_brightness = np.mean(image)
    return 70 <= avg_brightness <= 200
