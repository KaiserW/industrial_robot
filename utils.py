import gxipy as gx

import numpy as np
import cv2
import imutils

from sklearn import linear_model
from sklearn.externals import joblib

from datetime import datetime

from shapedetector import ShapeDetector


def ImageTaker():

    # 从大恒水星2相机获取图片
    device_manager = gx.DeviceManager()

    dev_num, dev_info_list = device_manager.update_device_list()

    # 未检测到设备
    if dev_num == 0:
        print("未检测到设备")

    else:
        print(dev_info_list)

    # 相机对象（取index为1的设备）
    cam = device_manager.open_device_by_index(1)

    # 开始采集图像
    cam.stream_on()

    raw_image = cam.data_stream[0].get_image()

    if raw_image is None:
        print("图像采集失败")

    else:
        print("Frame ID: {} | Height: {} | Width: {}".format(
            raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

    numpy_image = raw_image.get_numpy_array()
    if numpy_image is None:
        print("NumPy数组转换失败")

    # 停止采集图像
    cam.stream_off()

    # 存储图片
    img_filename = "ugrow_" + datetime.now().strftime("%Y%m%d%H%M%S")
    cv2.imwrite("images/{}.jpg".format(img_filename), numpy_image)

    # 读取图片
    image = cv2.imread("images/{}.jpg".format(img_filename))

    return image, img_filename


def CoordTransformer(image, img_filename):

    # 灰度化
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 高斯模糊
    blurred = cv2.GaussianBlur(gray, (5,5), 0)

    # 二值化
    _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)

    # 轮廓检测
    cnts = cv2.findContours(255-thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # 形状检测
    sd = ShapeDetector()

    output_image = image.copy()
    detections = []

    for c in cnts:

        shape = sd.detect(c)
        shape_dict = {"circle":0, "triangle":3, "rectangle":4}

        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        detections.append([shape_dict[shape],cY,cX])

        c = c.astype("int")
        cv2.drawContours(output_image, [c], -1, (0, 255, 0), 2)
        cv2.putText(output_image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)

    cv2.imwrite("images/{}_detected.jpg".format(img_filename), output_image)

    # 坐标变换
    clf = linear_model.Ridge()
    clf = joblib.load("model/coord_calib_ridge_regression.pkl")

    detect_array = np.array(detections, dtype="float32")

    print("-------------------------")
    print("Positions in Camera coord")
    print(detect_array)

    detect_array[:, 1:] = clf.predict(detect_array[:, 1:])
    detect_bytes = ["{:.0f}{:0>7.2f}{:0>7.2f}".format(row[0], row[1], row[2]).encode() 
                    for row in detect_array]

    print("Positions in Robot coord ")
    print(detect_bytes)
    print("-------------------------")

    return detect_bytes
