from collections import Counter
import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_image(img, title):
    plt.figure(figsize=(10, 8))
    if len(img.shape) == 2:
        plt.imshow(img, cmap="gray")
    else:
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis("off")
    plt.show()

def boxes_intersect(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

def calculate_magic_number(bounding_boxes):
    sizes = [w for _, _, w, h in bounding_boxes if w == h and w >= 40]
    if not sizes:
        return None
    size_counts = Counter(sizes)
    print("Size counts:", size_counts)

    # Find the size that results in the number of boxes closest to 24
    closest_size = min(size_counts, key=lambda size: abs(size_counts[size] - 24))

    return closest_size

def detect_boxes(img_path, tolerance):
    # Load the image
    img = cv2.imread(img_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Filter to only consider the left half of the image
    height, width = gray.shape
    gray = gray[:, :width // 2]

    # List to store bounding boxes
    bounding_boxes = []

    # Iterate through possible grayscale values with the given tolerance
    for value in range(0, 256):
        lower_bound = max(0, value - tolerance)
        upper_bound = min(255, value + tolerance)

        # Create a mask for the current grayscale value range
        mask = cv2.inRange(gray, lower_bound, upper_bound)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            bounding_boxes.append((x, y, w, h))

    # Filter bounding boxes based on size and shape
    valid_boxes = [box for box in bounding_boxes if box[2] == box[3] and box[2] >= 40]
    print(f"Total valid boxes: {len(valid_boxes)}")

    # Filter out intersecting boxes
    filtered_boxes = []
    for box in valid_boxes:
        intersecting_boxes = [
            valid_box
            for valid_box in filtered_boxes
            if boxes_intersect(box, valid_box)
        ]
        if not intersecting_boxes:
            filtered_boxes.append(box)
        else:
            # Keep the larger box
            largest_box = max(intersecting_boxes + [box], key=lambda b: b[2] * b[3])
            # Remove all intersecting boxes
            filtered_boxes = [
                b for b in filtered_boxes if b not in intersecting_boxes
            ]
            # Add the largest box
            filtered_boxes.append(largest_box)

    print(f"Total filtered boxes: {len(filtered_boxes)}")

    # Calculate the magic number
    magic_number = calculate_magic_number(filtered_boxes)
    if magic_number is None:
        print("No valid bounding boxes found.")
        return

    print(f"Magic number (box size): {magic_number}")

    # Filter bounding boxes based on the magic number
    final_boxes = [
        box
        for box in filtered_boxes
        if box[2] == magic_number and box[3] == magic_number
    ]
    print(f"Total boxes with magic number size: {len(final_boxes)}")

    # Draw the bounding boxes on the original image
    for x, y, w, h in final_boxes:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

    # Show the image with detected bounding boxes
    # Uncomment the following line to display the image
    # show_image(img, f"Detected Bounding Boxes with Tolerance {tolerance}")

    # Print the coordinates of the bounding boxes
    # Uncomment the following lines to print the coordinates
    # for i, (x, y, w, h) in enumerate(final_boxes):
    #     print(f"Box {i+1}: x={x}, y={y}, width={w}, height={h}")

    return final_boxes

def calculate_top_left_and_size(boxes):
    if not boxes:
        raise ValueError("No boxes provided.")

    # Sort boxes by top-left coordinate
    boxes = sorted(boxes, key=lambda box: (box[1], box[0]))

    # Calculate the top-left most coordinate
    top_left_x = min(box[0] for box in boxes)
    top_left_y = min(box[1] for box in boxes)

    size = boxes[0][2]

    return (top_left_x, top_left_y), size

def calculate_spacing(boxes):
    if not boxes:
        raise ValueError("No boxes provided.")

    # Sort boxes by top-left coordinate
    boxes = sorted(boxes, key=lambda box: (box[1], box[0]))

    # Calculate the spacing between boxes
    spacing = boxes[1][0] - (boxes[0][0] + boxes[0][2])

    return spacing

def infer_grid_size(boxes):
    if not boxes:
        raise ValueError("No boxes provided.")

    # Sort boxes by top-left coordinate
    boxes = sorted(boxes, key=lambda box: (box[1], box[0]))

    # Calculate the number of columns and rows
    num_columns = len(set(box[0] for box in boxes))
    num_rows = len(set(box[1] for box in boxes))

    return num_rows, num_columns

def main(image_path, tolerance=21):
    final_boxes = detect_boxes(image_path, tolerance)

    if not final_boxes:
        print("No valid bounding boxes found.")
    else:
        print("Bounding boxes found.")
        print("Calculating grid properties...")

        location, size = calculate_top_left_and_size(final_boxes)
        spacing = calculate_spacing(final_boxes)
        grid = infer_grid_size(final_boxes)

        output = {
            "location": location,
            "size": [size, size],
            "spacing": [spacing, spacing],
            "grid": grid,
        }
        return output

if __name__ == "__main__":
    image_path = "src/screenshot-analyzer-tests/screenshot.png"
    tolerance = 21
    output = main(image_path, tolerance)
    print(output)
