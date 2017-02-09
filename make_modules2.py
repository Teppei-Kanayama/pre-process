#-*- coding: utf-8 -*-
import os
import math

from PIL import Image
import numpy as np
from scipy import ndimage as ndi

import matplotlib.pyplot as plt #ヒストグラムの描画に使用
from scipy.misc import imsave #出力にのみ使用
import cv2 #bounding boxの描画に使用

from skimage import transform

def gaussian(img, sigma):
    return ndi.gaussian_filter(img, sigma)

def decide_threshold(img):
    threshold = 0
    tmp = 0
    for thresh_candidate in range(128):
        thresh_filter = img < thresh_candidate
        thresh_filter_ = img >= thresh_candidate

        omega1 = thresh_filter.sum()
        m1 = (img * thresh_filter).sum() / omega1
        omega2 = thresh_filter_.sum()
        m2 = (img * thresh_filter_).sum() / omega2

        numerator = omega1 * omega2 * (m1 - m2) ** 2
        if numerator > tmp:
            tmp = numerator
            threshold = thresh_candidate
    return threshold

def gray2bin(img, filtering=True, sigma=1): #TODO: gaussian()とotsu()を自前で作る。
    """Convert gray-scale image to binary image.

    # Input shape
        2D ndarray with shape: `(height, width)`

    # Output shape
        2D ndarray with shape: `(height, width)`

    # Arguments
        img: target image to be binarized
        filterling (optional): if you use gaussian filter before binarize, set this flag True
        sigma (optional): the hyper-parameter of gaussian filter
    """

    if filtering and sigma is not 0:
        img = gaussian(img, sigma=sigma)

    threshold = decide_threshold(img)
    return img >= threshold

def bbox(img):
    """Search bounding-box into binarized image

    # Input shape
        2D ndarray with shape: `(height, width)`

    # Output shape
        two lists which contains two elements: `[x1, y1], [x2, y2]`

    # Arguments
        img: target image
    """

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
        top_left = [min_width, min_height]
        bottom_right = [max_width, max_height]
    except UnboundLocalError:
        top_left = [0, 0]
        bottom_right = [width, height]
    return top_left, bottom_right


def draw_box(img, bbox):
    #太さ1の四角形を描く
    bounded_img = np.array(img).astype(np.uint8) * 255
    cv2.rectangle(bounded_img, (bbox[0][0], bbox[0][1]), (bbox[1][0], bbox[1][1]), (255, 255, 255), 1)
    return bounded_img

def resize(img, output_shape, bbox=None, locate="center", keep_shape=True, order=0): #TODO: resize関数を自前で作る。
    #output_shapeは正方形の場合しか想定していない。
    #bbox = ((左上のx座標，左上のy座標)，（右下のｘ座標，右下のｙ座標))
    """Resize operation for binary image.

    # Input shape
        2D ndarray with shape: `(height, width)`

    # Output shape
        2D ndarray with shape: `(height, width)`

    # Arguments
        img: target image to be resized
        output_shape: the shape of output image
        bbox (optional): the coordinate of bounding box (upper left and downer right)
        locate (optional): the location of the character. ("center" or "left" or "right")
        keep_shape (optional): if you need not to keep the character's shape, set this argument False
        order (optional): the method of completion method. (0~5)
    """
    padding_size = 100
    if bbox == None:
        return transform.resize(img, output_shape, order=order)

    width = bbox[1][0] - bbox[0][0]
    height = bbox[1][1] - bbox[0][1]

    if keep_shape == False:
        img = img[bbox[0][1]:bbox[0][1]+height, bbox[0][0]:bbox[0][0]+width]
        return transform.resize(img, output_shape, order=order)

    if height >= width:
        for i in range(2):
            for j in range(2):
                bbox[i][j] += padding_size
        img = np.lib.pad(img, padding_size, 'constant', constant_values=False)
        if locate == "left":
            img = img[bbox[0][1]:bbox[0][1]+height, bbox[0][0]:bbox[0][0]+height]
        elif locate == "center":
            img = img[bbox[0][1]:bbox[0][1]+height, bbox[0][0]-(height-width)/2:bbox[0][0]+(height+width)/2]
        elif locate == "right":
            img = img[bbox[0][1]:bbox[0][1]+height, bbox[1][0]-height:bbox[1][0]]
        else:
            raise NameError("such a location does not exist.")
    else:
        img = img[bbox[1][1]-width:bbox[1][1], bbox[0][0]:bbox[0][0]+width]

    resized_img = transform.resize(img, output_shape, order=order)
    if order is not 0:
        resized_img = gray2bin(resized_img, filtering=False)
    return resized_img

def draw_histogram(img, filename):
    x = img.flatten()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.hist(x, bins=256)
    ax.set_title(filename)
    ax.set_xlabel('gray value')
    ax.set_ylabel('freq')
    plt.savefig(filename)

def main():
    data = {}
    data['path'] = "../ETL_sample/images/ETL1/0/"
    data['background'] = 1
    data['path'] = "../ETL_sample/images/ETL7/ETL7SC_2/"
    data['background'] = 1
    #data_path = "../ETL_sample/images/ETL8G/A.HIRA/"
    #background = 1 #背景が黒なら1
    filenames = os.listdir(data['path'])

    # 画像の読み込み
    for filename in filenames:
        print filename
        if data['background'] == 1:
            img = np.array(Image.open(data['path'] + filename))
            print(img.dtype)
        else:
            img = np.array(Image.open(data['path'] + filename))

        #draw_histogram(img, './histogram_yu/' + filename)

        img = gray2bin(img, sigma=1)
        top_left, bottom_right = bbox(img)
        #img = draw_box(img, (top_left, bottom_right))
        img = resize(img, (28, 28), [top_left, bottom_right], locate="right", order=0)
        imsave('./edited_image/' + filename, img)

if __name__ == "__main__":
    main()
