# coding=utf-8

import cv2
import numpy as np
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import geojson


class Vector:
    longitude = None
    latitude = None
    gray_array = None
    width, height = 0, 0
    min_area = 25

    def __init__(self, longitude, latitude, gray):
        self.longitude = longitude
        self.latitude = latitude
        self.gray_array = gray
        self.height, self.width = gray.shape

    def contours(self, min_sect, max_sect):
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
            if contour_areas[i] > self.min_area:
                find_contours.append(contours[i])
        return find_contours

    def __contour2coordinates__(self, contour):
        coordinate = []
        c = np.int32(contour)
        for c2 in c:
            [[y, x]] = c2
            lon = float(self.longitude[x, y])
            lat = float(self.latitude[x, y])
            coordinate.append([lon, lat])
        return coordinate

    def polygons(self, min_sect, max_sect, simplify=0):
        polygons = []
        contours = self.contours(min_sect, max_sect)
        for c in contours:
            coordinates = self.__contour2coordinates__(c)
            p = Polygon(coordinates)
            if simplify > 0:
                p = p.simplify(simplify)
            polygons.append(p)
        return polygons

    def all_features(self, sections=None, simplify=0):
        features = []
        if sections is None:
            data = self.gray_array
            sections = np.arange(data.min(), data.max(), (data.max() - data.min()) / 20)
        for i in range(len(sections) - 1):
            polygons = self.polygons(sections[i], sections[i + 1], simplify=simplify)
            for p in polygons:
                feature = geojson.Feature(geometry=p)
                feature.properties['min_value'] = sections[i]
                feature.properties['max_value'] = sections[i + 1]
                features.append(feature)
        return features
