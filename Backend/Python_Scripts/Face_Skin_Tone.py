import stone 
import cv2 
import numpy as np
from json import dumps
import os
import sys

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    if len(hex_code)!= 6:
        raise ValueError("Invalid hex code. Must be 6 characters long (e.g., 'EDBEAB').")
    try:
        return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError("Invalid hex code. Contains non-hexadecimal characters.")

def classify_undertone_from_rgb(rgb_tuple):
    R, G, B = rgb_tuple

    scaled_R = R / 1.61
    
    # New condition: If the difference between scaled_R and B is less than 5, it's Neutral.
    # (Using 5 covers the condition for less than 2 as well)
    if abs(scaled_R - B) < 5:
        return "Neutral"
    
    # Apply the original classification rules if not neutral by difference
    if scaled_R > B:
        return "Warm"
    elif scaled_R < B or B > R:
        return "Cool"
    else:
        return "Neutral"

def get_undertone_lab(hex_color):
    try:
        rgb_values = hex_to_rgb(hex_color)
        return classify_undertone_from_rgb(rgb_values)
    except ValueError as e:
        print(f"Error processing hex code {hex_color}: {str(e)}", file=sys.stderr)
        return "Neutral"  # Default to neutral if there's an issue

def detect_and_analyze_face(image_path):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        return {"error": f"Could not read image {image_path}"}
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # Check if faces were detected
    if len(faces) == 0:
        return {"error": "No faces detected in the image"}
    
    all_results = []  # Store results for all faces
    
    # For each detected face
    for i, (x, y, w, h) in enumerate(faces):
        # Crop the face with a bit of padding (20% on each side)
        padding_x = int(w * 0.2)
        padding_y = int(h * 0.2)
        
        # Make sure we don't go outside image boundaries
        start_x = max(0, x - padding_x)
        start_y = max(0, y - padding_y)
        end_x = min(img.shape[1], x + w + padding_x)
        end_y = min(img.shape[0], y + h + padding_y)
        
        # Crop the face
        face_img = img[start_y:end_y, start_x:end_x]
        
        # Save the cropped face temporarily
        temp_face_path = f"temp_face_{i}.jpg"
        cv2.imwrite(temp_face_path, face_img)
        
        # Analyze with stone
        try:
            result = stone.process(temp_face_path, image_type="color", return_report_image=False)
            
            # Extract skin tone information
            skin_tone_hex = None
            dominant_color_hex = None
            
            if "faces" in result and result["faces"]:
                face_data = result["faces"][0]
                skin_tone_hex = face_data.get("skin_tone", "")
                dominant_colors = face_data.get("dominant_colors", [])
                dominant_color_hex = dominant_colors[0]["color"] if dominant_colors else ""
                accuracy = face_data.get("accuracy", 0)
                
                if skin_tone_hex:
                    undertone = get_undertone_lab(dominant_color_hex)
                    
                    # Store the result
                    all_results.append({
                        "face_id": i+1,
                        "skin_tone": skin_tone_hex,
                        "dominant_color": dominant_color_hex,
                        "undertone": undertone,
                        "accuracy": accuracy
                    })
            
        except Exception as e:
            print(f"Error analyzing face {i+1}: {str(e)}", file=sys.stderr)
        
        # Clean up the temporary file
        if os.path.exists(temp_face_path):
            os.remove(temp_face_path)
    
    return {"faces": all_results}

if __name__ == "__main__":
    # Check if image path is provided as command line argument
    if len(sys.argv) != 2:
        print(dumps({"error": "Image path not provided. Usage: python Face_Skin_Tone.py <image_path>"}))
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Process the image and get results
    results = detect_and_analyze_face(image_path)
    
    # Print results as JSON to stdout (will be captured by the Node.js process)
    print(dumps(results))