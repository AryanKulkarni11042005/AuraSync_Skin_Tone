import stone 
import cv2 
from json import dumps # Optional


image_path = "images\Jim_Parsons.jpeg"

result = stone.process(image_path, image_type="color", return_report_image=True)

report_images = result.pop("report_images")  # obtain and remove the report image from the `result`

face_id = 1
result_json = dumps(result)
print(result_json)  
cv2.imshow("Report Image", report_images[face_id])
cv2.waitKey(0)
cv2.destroyAllWindows()
  