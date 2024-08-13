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


def find_lock_button(img_path):
    # Load the image
    img = cv2.imread(img_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    show_image(gray, "Grayscale Image")
    
    # TODO: FIND LOCK BUTTON

def main(image_path):
    find_lock_button(image_path)

if __name__ == "__main__":
    image_path = "src/screenshot-analyzer-tests/screenshot.png"
    main(image_path)