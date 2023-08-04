import cv2
import numpy as np

ROW = 16
COLUMN = 6

# you need "puyo_sozai.png" in /img, that can be downlaoded from https://puyo.weakflour.net/puyo_sozai.png (as of 2023/08/04) 
# thanks to https://puyo-camp.jp/users/226991 
image = cv2.imread("./img/puyo_sozai.png", -1)
original_height, original_width, _ = image.shape
height, width = original_height//ROW, original_width//COLUMN

for i in range(0, ROW):
    for j in range(0, COLUMN):
        img_array = image[i*height:i*height+height, j*width:j*width+width]
        cv2.imwrite(f"./img/{i}_{j}.png", img_array)