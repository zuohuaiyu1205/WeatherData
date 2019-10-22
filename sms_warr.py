# coding=utf-8

import Nio
import sys
import numpy as np
import geo_feature as geo

'''grid data of surface'''


class Surface:
    _file_ = None
    temperature = None
    temperature2 = None
    relative_humidity2 = None
    temperature_of_dew_point2 = None
    wind_speed = None
    wind_direction = None
    longitude = None
    latitude = None
    min_lon, max_lon = -360, 360
    min_lat, max_lat = -360, 360
    fresh = False

    def __init__(self, surface_file_name):
        self._file_ = Nio.open_file(surface_file_name)

    def init(self):
        self.temperature = self.get_array('TMP_P0_L1_GLC0', 273.15)
        self.temperature2 = self.get_array('TMP_P0_L103_GLC0', 273.15)
        self.relative_humidity2 = self.get_array('RH_P0_L103_GLC0')
        self.temperature_of_dew_point2 = self.get_array('DPT_P0_L103_GLC0', 273.15)
        wind_speed_u = self.get_array('UGRD_P0_L103_GLC0')
        wind_speed_v = self.get_array('VGRD_P0_L103_GLC0')
        self.wind_speed = np.sqrt(wind_speed_u * wind_speed_u + wind_speed_v * wind_speed_v)
        self.wind_direction = np.arcsin(wind_speed_u / self.wind_speed)
        self.longitude = self.get_array('ELON_P0_L1_GLC0')
        self.latitude = self.get_array('NLAT_P0_L1_GLC0')
        self.min_lon = self.longitude.min()
        self.max_lon = self.longitude.max()
        self.min_lat = self.latitude.min()
        self.max_lat = self.latitude.max()
        self._file_.close()
        self.fresh = True

    def get_temperature(self):
        return self.get_array('TMP_P0_L1_GLC0', 273.15)

    def get_image(self, data, sections):
        return geo.get_color_image(data, sections)

    def get_array(self, grid_name, delta=0):
        grid_array = self._file_.variables[grid_name]
        return grid_array.get_value().data - delta

    def get_geojson(self, array_name, sections=None):
        if not self.fresh:
            self.init()
        grid_array = self._file_.variables[array_name]
        return geo.get_geojson(grid_array, sections)

    def temperature_geojson(self, sections=None):
        if not self.fresh:
            self.init()
        return geo.get_geojson(self.temperature, sections)

    def wind_geojson(self, sections=None):
        if not self.fresh:
            self.init()
        return geo.get_geojson(self.wind_speed, sections)

    def humidity_geojson(self, sections=None):
        if not self.fresh:
            self.init()
        return geo.get_geojson(self.relative_humidity2, sections)

class High:
    def __init__(self, high_name):
        self._file_ = Nio.open_file(high_name)


if __name__ == '__main__':
    file_name = sys.argv[1]
    surface = Surface(file_name)
    temp = surface.get_temperature()
