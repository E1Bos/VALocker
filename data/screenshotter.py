## This file is used to take screenshots in game for debug and config purposes. It is not required to run the program.

import PIL.ImageGrab, PIL.Image
import time

def capture_images(totalimages, name, coords,offset=0):
    for i in range(totalimages):
        image = PIL.ImageGrab.grab(bbox=coords)
        image.save(f"temp_images/{name}{i+offset}.png")

def compare_images(totalimages, name, offset=0, analyze_all=True):
    if analyze_all == True:
        analyze_all = totalimages
    
    total_similar = [0 for _ in range(analyze_all)]
    for i in range(0, analyze_all):
        print(f'Comparing image {i} to other images')
        image1 = PIL.Image.open(f"temp_images/{name}{i+offset}.png").tobytes()
        for j in range(totalimages):
            image2 = PIL.Image.open(f"temp_images/{name}{j+offset}.png").tobytes()
            if image1 == image2 and i!=j:
                total_similar[i] += 1
            # elif i!=j:
            #     print(f"Image {i} and {j} are different")
            

    for index, item in enumerate(total_similar):
        print(f'Image {index} is similar to {item} other images')

image_name = 'agent_screen_'
time.sleep(4)
capture_images(50, image_name, (945, 866, 955, 867), 1)
compare_images(51, image_name)
