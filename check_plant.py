import cv2
import numpy as np
import argparse
import os

def extract_frames(video_path, interval=30):
    """Extract frames from video at specified intervals"""
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

def save_first_frame(video_path, output_path=None, format="jpg"):
    """Extract and save the first frame of the video"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError("Could not read the first frame from the video")
    
    # Create default output path if not provided
    if output_path is None:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = f"{video_name}_first_frame.{format.lower()}"
    
    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the image
    success = cv2.imwrite(output_path, frame)
    if not success:
        raise ValueError(f"Failed to save image to {output_path}")
    
    return output_path

def is_plant_present(frame, green_threshold=1000):
    """Check if plant is present in a frame using color analysis"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define range for green colors (adjust these values as needed)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    
    # Create mask and count green pixels
    mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pixels = cv2.countNonZero(mask)
    
    return green_pixels > green_threshold

def video_contains_plant(video_path, interval=30, confidence_threshold=0.3):
    """Main function to check plant presence in video"""
    try:
        frames = extract_frames(video_path, interval)
        if not frames:
            return False
        
        plant_frames = 0
        for frame in frames:
            if is_plant_present(frame):
                plant_frames += 1
                
        confidence = plant_frames / len(frames)
        return confidence >= confidence_threshold
    
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return False

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Check if video contains plants and save first frame")
    # parser.add_argument("video_path", help="Path to input video file")
    # parser.add_argument("--interval", type=int, default=30, 
    #                    help="Frame extraction interval (default: 30)")
    # parser.add_argument("--confidence", type=float, default=0.3,
    #                    help="Confidence threshold (0-1) for plant detection (default: 0.3)")
    # parser.add_argument("--save-frame", action="store_true", 
    #                    help="Save the first frame of the video")
    # parser.add_argument("--output", type=str, default=None,
    #                    help="Output path for the saved frame (default: video_name_first_frame.jpg)")
    # parser.add_argument("--format", type=str, choices=["jpg", "png"], default="jpg",
    #                    help="Format to save the image (jpg or png)")
    # args = parser.parse_args()
    
    # Save the first frame if requested
    
    # Check for plant presence
    result = video_contains_plant(
        "C:\\Users\\Prajwal\\Downloads\\VID20250515192543.mp4"
    )
    if result:
        try:
            saved_path = save_first_frame("C:\\Users\\Prajwal\\Downloads\\Presentation1.mp4", "extracted_frame.png", "png")
            print(f"First frame saved to: {saved_path}")
        except Exception as e:
            print(f"Error saving first frame: {str(e)}")
    
    print(f"Plant detected: {'YES' if result else 'NO'}")
