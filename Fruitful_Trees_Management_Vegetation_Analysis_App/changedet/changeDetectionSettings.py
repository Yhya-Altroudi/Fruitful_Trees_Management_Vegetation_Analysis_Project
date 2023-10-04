import enum


# NDVI Settings
class NDVI_SETTINGS(enum.Enum):

    LANDSAT7_OLD_NAME = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']
    LANDSAT7_NEW_NAME = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']
    MERGE_BANDS_NAMES = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']

    LANDSAT7_NAME = "LANDSAT/LE07/C02/T1_L2"
    L7_OPTICAL_BANDS_NAME = "SR_B."
    L7_THERMAL_BANDS_NAME = "ST_B6"

    LANDSAT8_NAME = "LANDSAT/LC08/C02/T1_L2"
    L8_OPTICAL_BANDS_NAME = "SR_B."
    L8_THERMAL_BANDS_NAME = "ST_B.*"

    VIS_PARAMS = {"min": -1, "max": 1,
                  "palette": ["red", "white", "green"]}


# BAI Settings
class BAI_SETTINGS(enum.Enum):

    LANDSAT7_OLD_NAME = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']
    LANDSAT7_NEW_NAME = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']
    MERGE_BANDS_NAMES = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']

    LANDSAT7_NAME = "LANDSAT/LE07/C02/T1_L2"
    L7_OPTICAL_BANDS_NAME = "SR_B."
    L7_THERMAL_BANDS_NAME = "ST_B6"

    LANDSAT8_NAME = "LANDSAT/LC08/C02/T1_L2"
    L8_OPTICAL_BANDS_NAME = "SR_B."
    L8_THERMAL_BANDS_NAME = "ST_B.*"

    VIS_PARAMS = {'min': 0, 'max': 400,
                  'palette': ['green', 'blue', 'yellow', 'red']}


# Change Detection Settings
class CHANGE_DETECTION_SETTINGS(enum.Enum):

    LANDSAT8_NAME = "LANDSAT/LC08/C02/T1_L2"
    L8_OPTICAL_BANDS_NAME = "SR_B."
    L8_THERMAL_BANDS_NAME = "ST_B.*"

    VIS_PARAMS = {'palette': ['0000ff', '00ff00', '0000ff', 'ff0000']}

# time series settings


class TIME_SERIES_SETTINGS(enum.Enum):

    LANDSAT8_NAME = "LANDSAT/LC08/C02/T1_L2"
    L8_OPTICAL_BANDS_NAME = "SR_B."
    L8_THERMAL_BANDS_NAME = "ST_B.*"

    VIS_PARAMS = {}
