# coding=utf-8

import sys
import cv2
import geojson
import sms_warr as sms
import Ngl


def read_features():
    return None


if __name__ == '__main__':
    file_name = sys.argv[1]
    nio = sms.SmsWarr(file_name)
    temp = nio.get_temperature()
    print(temp)
    Ngl.contour()