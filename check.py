import cv2
import os
import numpy as np

def extract_frames(video_path, interval=30):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    frames = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval == 0:
            frames.append(frame)
        frame_count += 1
    cap.release()
    return frames

def is_plant_present(frame, green_threshold=300):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pixels = cv2.countNonZero(mask)
    return green_pixels > green_threshold

def is_frame_blurry(frame, threshold=50):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold

def frame_difference_score(prev_frame, next_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(prev_gray, next_gray)
    return np.mean(diff)

def detect_low_motion(frames, diff_threshold=3):
    if len(frames) < 2:
        return True  # not enough info
    differences = []
    for i in range(len(frames) - 1):
        score = frame_difference_score(frames[i], frames[i+1])
        differences.append(score)
    avg_diff = np.mean(differences)
    return avg_diff < diff_threshold

def video_contains_plant(video_path, interval=30, confidence_threshold=0.3):
    try:
        frames = extract_frames(video_path, interval)
        if not frames:
            return False

        plant_frames = 0
        for frame in frames:
            if not is_plant_present(frame):
                continue
            if is_frame_blurry(frame):
                continue
            plant_frames += 1

        confidence = plant_frames / len(frames)

        # Add motion check: if almost no motion, it's likely a screen video
        is_low_motion = detect_low_motion(frames)

        return confidence >= confidence_threshold and not is_low_motion

    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return False

def save_first_frame(video_path, output_path=None, format="jpg"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise ValueError("Could not read the first frame from the video")

    if output_path is None:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = f"{video_name}_first_frame.{format.lower()}"

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    success = cv2.imwrite(output_path, frame)
    if not success:
        raise ValueError(f"Failed to save image to {output_path}")

    return output_path
