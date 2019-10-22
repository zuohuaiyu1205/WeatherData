# coding=utf-8

import cv2
import geojson as geo
import numpy as np
import config
from shapely.geometry import Polygon


def get_color_image(data, sections=None, colors=None, buffer_radius=0):
    w, h = data.shape
    img = np.ones((w, h, 3), dtype=np.uint8) * 255
    if colors is None:
        colors = config.temperature_colors
    if sections is None:
        sections = np.arange(data.min(), data.max(), (data.max() - data.min()) / 20)
    for i in range(len(sections) - 1):
        contours = get_contours(data, sections[i], sections[i + 1])
        if buffer_radius > 0:
            contours = _buffer(contours, buffer_radius)
        r, g, b = colors[i]
        img = cv2.drawContours(img, contours, -1, (r, g, b), -1)
    return img


"""
    get contours of temperature.
    :gray: 2D array of the image.
    :min_sect: min value of the temperature
    :max_sect: max value of the temperature
    :ratio: if the contour is smaller than ratio * max contour, discard it
    :min_area: if the contour is smaller than min_area, discard it
"""


def get_contours(gray, min_sect, max_sect, ratio=0, min_area=15):
    data = gray.copy()
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
        if contour_areas[i] / max_contour_area > ratio and contour_areas[i] > min_area:
            find_contours.append(contours[i])
    return find_contours


def get_features(data, sections):
    features = []
    if sections is None:
        sections = np.arange(data.min(), data.max(), (data.max() - data.min()) / 20)
    for i in range(len(sections) - 1):
        contours = get_contours(data, sections[i], sections[i + 1])
        for contour in contours:
            polygon = _contour2polygon(contour)
            feature = geo.Feature(geometry=polygon);
            feature.properties['min_value'] = sections[i]
            feature.properties['max_value'] = sections[i + 1]
            features.append(feature)
    return features


def get_geojson(data, sections):
    return geo.dumps(get_features(data, sections))


def get_json_list(data, sections):
    json = []
    features = get_features(data, sections)
    for f in features:
        json.append(geo.dumps(f))
    return json


def __contour2coordinates__(contour):
    coordinate = []
    c = np.int32(contour)
    for c2 in c:
        [[x, y]] = c2
        coordinate.append([float(x), float(y)])
    [[x, y]] = c[0]
    coordinate.append([float(x), float(y)])
    return coordinate


def __polygon2coordinates__(polygon):
    return polygon.coordinates[0]


def __coordinates2contour__(coordinates, data_type=np.int32):
    length = len(coordinates) - 1
    contour = np.zeros((length, 1, 2), dtype=data_type)
    for i in range(length):
        [x, y] = coordinates[i]
        contour[i] = [x, y]
    return contour


def _contour2polygon(contour):
    coordinates = __contour2coordinates__(contour)
    p = geo.Polygon()
    p.coordinates = []
    p.coordinates.append(coordinates)
    p.update()
    if p.errors() is None:
        return p
    return None


def _buffer(contours, radius):
    for i in range(len(contours)):
        coordinates = __contour2coordinates__(contours[i])
        p = Polygon(coordinates)
        coordinates = list(p.buffer(radius).exterior.coords)
        contours[i] = __coordinates2contour__(coordinates)
    return contours


def draw(contour):
    x = contour[:, 0, 0]
    y = contour[:, 0, 1]
    return x, y


# def _contour2polygon(contour):
#     coordinates = []
#     c = np.int32(contour)
#     for c2 in c:
#         [[x, y]] = c2
#         coordinates.append([float(x), float(y)])
#     [[x, y]] = c[0]
#     coordinates.append([float(x), float(y)])
#     polygon = Polygon(coordinates)
#     return polygon
#
# def _polygon2contour(polygon, data_type=np.int32):
#     coordinates = list(polygon.exterior.coords)
#     length = len(coordinates) - 1
#     contour = np.zeros((length, 1, 2), dtype=data_type)
#     for i in range(length):
#         (x, y) = coordinates[i]
#         contour[i] = [x, y]
#     return contour

# def resize(features, latitude, longitude):


class Polygon:

    def __init__(self, data):
        grid = data

    # def get_polygons(self, data, sections):
