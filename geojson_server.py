from flask import Flask, jsonify, request, make_response, abort
import sms_warr as sms
import urllib.parse as parse
import base64
import numpy as np
import cv2
import sys
import os

PORT = 8000
HOST = '127.0.0.1'

app = Flask(__name__)

MY_URL = '/weather/geojson/'


@app.route(MY_URL + 'post/', methods=['GET'])
def get_task():
    parameters = request.args.to_dict()
    if not check(parameters):
        abort(404)
    return do(parameters)


def check(parameters):
    keys = ['file_path', 'var_name', 'sections']
    for key in keys:
        if key not in parameters:
            return False
    return True


def do(parameters):
    file_path = str(parameters["file_path"])
    var_name = str(parameters["var_name"])
    if parameters["sections"] == "":
        sections = None
    else:
        sections = [int(i) for i in parameters["sections"].split(',')]
    dir_path = "/home/gis/PycharmProjects/WeatherData/data/"
    if not os.path.exists(dir_path + file_path):
        return "can not find the weather file " + file_path
    surface = sms.Surface(dir_path + file_path)
    if var_name == "temperature":
        return surface.temperature_geojson(sections=sections)
    elif var_name == "wind":
        return surface.wind_geojson(sections=sections)
    elif var_name == "humidity":
        return surface.humidity_geojson(sections=sections)

    # str_image = parse.unquote(str_image)
    # if str_image.startswith('b\'') and str_image.endswith('\''):
    #     str_image = str_image[2:-1]
    # base64_string = parse.unquote(str_image)
    # pix = np.fromstring(base64.b64decode(base64_string), np.uint8)
    # image = cv2.imdecode(pix, 3)
    # semantic = str(parameters["semantic"])
    # semantic = parse.unquote(semantic)
    #
    # return decoder.get_result(image, semantic)


@app.route(MY_URL + 'post/', methods=['POST'])
def post_task():
    parameters = request.form
    if not check(parameters):
        abort(404)
    return do(parameters)


# 404处理
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    argv_count = len(sys.argv)
    if argv_count == 1:
        app.run(host=HOST, port=PORT)
    elif argv_count == 2:
        app.run(host=sys.argv[1], port=PORT)
    elif argv_count == 3:
        app.run(host=sys.argv[1], port=sys.argv[2])
    else:
        print('IP and PORT are wrong.')
