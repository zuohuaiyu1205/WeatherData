# coding=utf-8

import cv2
import numpy as np
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point


class Vector:
    longitude = None
    latitude = None
    gray_array = None
    width, height = 0, 0

    def __init__(self, longitude, latitude, gray):
        self.longitude = longitude
        self.latitude = latitude
        self.gray_array = gray
        self.height, self.width = gray.shape

    def contours(self, min_sect, max_sect, min_area=15):
        data = self.gray_array.copy()
        self.width, self.height = data.shape
        binary = np.where(data >= min_sect, 1, 0) * np.where(data <= max_sect, 1, 0)
        binary = np.uint8(binary)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_contour_area = 0
        contour_areas = []
        for c in contours:
            area = cv2.contourArea(c)
            contour_areas.append(area)
            if area > max_contour_area:
                max_contour_area = area
        find_contours = []
        for i in range(len(contours)):
            if contour_areas[i] > min_area:
                find_contours.append(contours[i])
        return find_contours

    def __contour2coordinates__(self, contour):
        coordinate = []
        c = np.int32(contour)
        for c2 in c:
            [[x, y]] = c2
            lon = float(self.longitude[x, y])
            lat = float(self.latitude[x, y])
            coordinate.append([lon, lat])
        return coordinate

    def polygons(self, min_sect, max_sect):
        polygons = []
        contours = self.contours(min_sect, max_sect)
        for c in contours:
            coordinates = self.__contour2coordinates__(c)
            p = Polygon(coordinates)
            polygons.append(p)
        return polygons

