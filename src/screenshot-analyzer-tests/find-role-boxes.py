import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_image(image_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb

def create_mask(image_rgb, lower_bound, upper_bound):
    return cv2.inRange(image_rgb, lower_bound, upper_bound)

def find_contours(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def find_left_box(contours, size_threshold=(30, 30)):
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > size_threshold[0] and h > size_threshold[1]:
            return (x, y, w, h)
    return None

def find_right_box(contours, left_box):
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if (
            left_box
            and x > left_box[0] + left_box[2]
            and y < left_box[1] + left_box[3]
            and y + h > left_box[1]
        ):
            return (x, y, w, h)
    return None

def calculate_spacing(mask_dark_blue, left_box, right_box):
    start_x = left_box[0] + left_box[2]
    end_x = right_box[0]
    y_top = max(left_box[1], right_box[1])
    y_bottom = min(left_box[1] + left_box[3], right_box[1] + right_box[3])
    region_between_boxes = mask_dark_blue[y_top:y_bottom, start_x:end_x]
    spacing = cv2.countNonZero(region_between_boxes)
    return spacing

def main(image_path, target_rgb):
    image_rgb = load_image(image_path)
    
    height, width, _ = image_rgb.shape
    image_rgb = image_rgb[:, :width // 2]
    
    lower_dark_blue = np.array([50, 130, 180])
    upper_dark_blue = np.array([60, 140, 190])
    
    mask_left_box = create_mask(image_rgb, np.array(target_rgb) - 1, np.array(target_rgb) + 1)
    mask_dark_blue = create_mask(image_rgb, lower_dark_blue, upper_dark_blue)
    
    contours_left_box = find_contours(mask_left_box)
    contours_dark_blue = find_contours(mask_dark_blue)
    
    left_box = find_left_box(contours_left_box)
    right_box = find_right_box(contours_dark_blue, left_box)
    
    if left_box and right_box:
        spacing = calculate_spacing(mask_dark_blue, left_box, right_box)
        result = {
            "coords": [left_box[0], left_box[1]],
            "size": [left_box[2], left_box[3]],
            "spacing": [spacing, spacing],
        }
        return result
    else:
        print("Could not find both boxes to calculate spacing.")

if __name__ == "__main__":
    image_path = "src/screenshot-analyzer-tests/screenshot.png"
    target_rgb = [236, 232, 225]
    output = main(image_path, target_rgb)
    print(output)