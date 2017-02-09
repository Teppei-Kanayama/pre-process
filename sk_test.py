#-*- coding: utf-8 -*-
import os
from PIL import Image
import numpy as np

from scipy.misc import imsave #出力にのみ使用
import cv2

import skimage
from skimage import data
from skimage.morphology import disk
from skimage.filters import threshold_otsu, rank, gaussian
from skimage.util import img_as_ubyte

from skimage import transform
import math
import time

def thresh_otsu(img, isgaussian=True, sigma=1):
    #大津の方法
    if isgaussian:
        img = gaussian(img, sigma=sigma)

    radius = 15
    selem = disk(radius)

    local_otsu = rank.otsu(img, selem)
    try:
        threshold_global_otsu = threshold_otsu(img)
    except TypeError:
        threshold_global_otsu = 255

    global_otsu = img >= threshold_global_otsu
    #print(global_otsu.dtype)
    return global_otsu


def calc_sphere(img):
    # 画像の高さ、幅を取得
    height = img.shape[0]
    width = img.shape[1]

    #高さの最大値、最小値の計算
    #もうちょい良い実装ありそう
    flag = False
    for i in range(height):
        if np.sum(img, axis=1)[i] > 0:
            if flag == False:
                min_height = i
                flag = True
            max_height = i

    #幅の最大値、最小値
    #もうちょい良い実装ありそう
    flag = False
    for i in range(width):
        if np.sum(img, axis=0)[i] > 0:
            if flag == False:
                min_width = i
                flag = True
            max_width = i
    try:
        #sphere = (min_height, max_height, min_width, max_width)
        top_left = (min_width, min_height)
        bottom_right = (max_width, max_height)
    except UnboundLocalError:
        #sphere = (0, height, 0, width)
        top_left = (0, 0)
        bottom_right = (width, height)
    return top_left, bottom_right

"""
def draw_box(img, min_height, max_height, min_width, max_width):
    #太さ1の四角形を描く
    bounded_img = np.array(img)
    cv2.rectangle(bounded_img, (min_width, min_height), (max_width, max_height), (255, 255, 255), 1)
    return bounded_img
"""

def trim_image(img, min_height, max_height, min_width, max_width):
    #画像のトリミング
    trimed_img = img[min_height:max_height, min_width:max_width]
    return trimed_img

def resize_image(img, output_shape, method):
    #画像のリサイズ
    if method=="resize":
        return transform.resize(img, output_shape, order=0)
    elif method == "rescale":
        input_shape = img.shape
        return transform.rescale(img, (float(output_shape[0]) / input_shape[0], float(output_shape[1]) / input_shape[1]))
    elif method == "downscale_local_mean":
        input_shape = img.shape
        print(input_shape)
        print(output_shape)
        print(math.ceil(float(input_shape[0]) / output_shape[0]))
        print(math.ceil(float(input_shape[1]) / output_shape[1]))
        return transform.downscale_local_mean(img, (int(math.ceil(float(input_shape[0]) / output_shape[0])), int(math.ceil(float(input_shape[1]) / output_shape[1]))))

def main():
    data = {}
    data['path'] = "../ETL_sample/images/ETL1/0/"
    data['background'] = 1
    #data['path'] = "../ETL_sample/images/ETL7/ETL7SC_2/"
    #data['background'] = 1
    #data_path = "../ETL_sample/images/ETL8G/A.HIRA/"
    #background = 1 #背景が黒なら1
    filenames = os.listdir(data['path'])

    # 画像の読み込み
    for filename in filenames:
        print filename
        if data['background'] == 1:
            img = np.array(Image.open(data['path'] + filename))
        else:
            img = np.array(Image.open(data['path'] + filename))
        img = thresh_otsu(img)
        #img = resize_image(img, (28, 28), "resize")

        #img = skimage.morphology.binary_closing(img)
        top_left, bottom_right = calc_sphere(img)
        croped_height = croped_width = max(max_height - min_height, max_width - min_width)
        img = draw_box(img.astype(np.uint8) * 255, min_height, max_height, min_width, max_width)
        img = trim_image(img, min_height, min_height + croped_height, min_width, min_width + croped_width)
        img = resize_image(img, (28, 28), "resize")
        #img = thresh_otsu(img)
        imsave('./edited_image/' + filename, img)

if __name__ == "__main__":
    main()
