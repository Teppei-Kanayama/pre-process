#-*- coding: utf-8 -*-
import os
from PIL import Image
import numpy as np

from scipy.misc import imsave #出力にのみ使用
import cv2
import sys
reload(sys)

# 画像の読み込み
#img = np.array( Image.open('../ETL_sample/images/ETL1/0/ETL1_1_1002_0.png') )

def thresh_otsu(img):
    #大津の方法
    ret,thresh_img = cv2.threshold(img,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    return thresh_img
    
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
        sphere = (min_height, max_height, min_width, max_width)
    except UnboundLocalError:
        sphere = (0, height, 0, width)
    return sphere
        
            
def draw_box(img, min_height, max_height, min_width, max_width):
    #太さ1の四角形を描く
    bounded_img = np.array(img)
    cv2.rectangle(bounded_img, (min_width, min_height), (max_width, max_height), (255, 255, 255), 1)
    return bounded_img

def trim_image():
    #画像のトリミング
    #trimed_img = img[min_height:max_height, min_width:max_width]
    pass

def main():
    
    #data_path = "../ETL_sample/images/ETL1/0/"
    #data_path = "../ETL_sample/images/ETL7/ETL7SC_2/"
    #data_path = "../ETL_sample/images/ETL8G/A.HIRA/"
    #sys.setdefaultencoding('UTF-8')
    #print sys.getdefaultencoding()
    data_path = "../samples/mu/"
    background = 1 
    filenames = os.listdir(data_path)
    
    # 画像の読み込み
    for filename in filenames:
        print filename
        if background == 1:
            img = np.array( Image.open((data_path + filename).decode('UTF-8')))
        else:
            img = 255 - np.array( Image.open(data_path + filename) )
        img = thresh_otsu(img)
        min_height, max_height, min_width, max_width = calc_sphere(img)
        bounded_img = draw_box(img, min_height, max_height, min_width, max_width)
        imsave(('./edited_image/' + filename).decode('UTF-8'), bounded_img)

#imsave('./edited_image/test2.jpg', trimed_img)
                    
if __name__ == "__main__":
    main()
