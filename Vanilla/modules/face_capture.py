import cv2
from config import RESIZED_DIM

def capture_face_variations(face_roi, output_path, count, pose):
    for angle in [-10, 0, 10]:
        M = cv2.getRotationMatrix2D((face_roi.shape[1]/2, face_roi.shape[0]/2), angle, 1)
        rotated = cv2.warpAffine(face_roi, M, (face_roi.shape[1], face_roi.shape[0]))
        resized = cv2.resize(rotated, RESIZED_DIM)
        cv2.imwrite(f'{output_path}/{count:03d}_{pose}.jpg', resized)
        count += 1
    return count
