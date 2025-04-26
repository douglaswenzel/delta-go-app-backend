from config import MIN_EYE_AREA, MIN_EYE_SIZE_RATIO

def validate_eyes(eye_regions):
    if len(eye_regions) < 2:
        return False

    eye_areas = [w * h for (_, _, w, h) in eye_regions]
    if any(area < MIN_EYE_AREA for area in eye_areas):
        return False

    size_ratio = max(eye_areas) / min(eye_areas)
    return size_ratio <= MIN_EYE_SIZE_RATIO
