import stone 
import cv2 
import numpy as np
from json import dumps
import os

def detect_and_analyze_face(image_path):
    print(f"Processing image: {image_path}")
    
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # Check if faces were detected
    if len(faces) == 0:
        print("No faces detected in the image.")
        return
    
    print(f"Found {len(faces)} faces")
    
    # For each detected face
    for i, (x, y, w, h) in enumerate(faces):
        # Draw rectangle around face (for visualization)
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
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
        
        # Show the cropped face
        cv2.imshow(f"Detected Face {i+1}", face_img)
        
        # Analyze with stone
        result = stone.process(temp_face_path, image_type="color", return_report_image=True)

        report_images = result.pop("report_images")  # obtain and remove the report image from the `result`

        face_id = 1
        result_json = dumps(result)
        print(result_json)  
        cv2.imshow("Report Image", report_images[face_id])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Clean up the temporary file
        if os.path.exists(temp_face_path):
            os.remove(temp_face_path)
    
    # Show the original image with face rectangles
    cv2.imshow("Detected Faces", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    skin_tone_hex = None
    dominant_color_hex = None
    if "faces" in result and result["faces"]:
                face_data = result["faces"][0]
                skin_tone_hex = face_data.get("skin_tone_hex")
                dominant_color_hex = face_data.get("dominant_color_hex")
    if skin_tone_hex:
                    undertone = get_undertone_lab(skin_tone_hex)
                    print(undertone)

# Process a single image
image_path = "images/Adam_Samberg.jpeg"
detect_and_analyze_face(image_path)
def get_undertone_lab(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    bgr = np.uint8([[[b, g, r]]])
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[0][0]
    
    # a channel: green (low) to red (high)
    # b channel: blue (low) to yellow (high)
    a, b = lab[1], lab[2]

    if a > b + 5:
        return "Warm"
    elif b > a + 5:
        return "Cool"
    else:
        return "Neutral"
# To process multiple images, uncomment and modify this section:
"""
image_paths = [
    "images/Jim_Parsons.jpeg",
    "theRock.jpg",
    # Add more image paths here
]

for path in image_paths:
    detect_and_analyze_face(path)
    print("-" * 50)
"""