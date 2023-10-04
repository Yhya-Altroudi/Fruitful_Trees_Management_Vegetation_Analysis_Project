import ee
import math


# Landsat_Analyser: class for performing data analysis operations on landsat 7&8 datasets
class Landsat_Analyser:

    '''
    Landsat_Analyser: class for performing data analysis operations on landsat 7&8 datasets
    '''

    def __init__(self, start_date, end_date, study_region):
        '''
        Landsat_Analyser constractor
        '''
        self._start_date = start_date
        self._end_date = end_date
        self._study_region = study_region

        self._marged_images = None

    def get_image(self):
        '''
        get self.image value
        '''
        return self._image

    def set_image(self, image):
        '''
        set ee.image tow class image
        '''
        self.__image = image
        return

    def _applyScaleFactors(self, image, opticalBandsName: str, thermalBandsName: str):
        '''
        apply Scale factors and offsets on optical and thermal bands of landsat 7&8 

        '''

        opticalBands = image.select(opticalBandsName).multiply(
            0.0000275).add(-0.2)  # l8:'SR_B.' ,l7: 'SR_B.'
        thermalBands = image.select(thermalBandsName).multiply(
            0.00341802).add(149.0)  # l8: 'ST_B.*' ,l7: 'ST_B6'

        return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)

    def _maskSrClouds(self, image):
        '''
        apply cloud and saturation masking
        '''

        # Bit 0 - Fill
        # Bit 1 - Dilated Cloud
        # Bit 2 - Cirrus
        # Bit 3 - Cloud
        # Bit 4 - Cloud Shadow
        qaMask = image.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
        saturationMask = image.select('QA_RADSAT').eq(0)

        return image.updateMask(qaMask).updateMask(saturationMask)

    def rename(self, image, old_name, new_name):
        '''
        rename and select specific bands on images
        default values are for mage landsat7 and landsat8 have the same main bands name
        '''
        return image.select(old_name, new_name)

    def get_ScFiltMasked_imageColl(self, sat_name: str, opticalBandsName: str, thermalBandsName: str):
        '''
        get sat_name image collection
        Apply bound filter
        Select images dates
        Filter landsat image collection by cloud cover
        Apply cloud masking
        Apply the scaling factor function on the set of image collection.
        '''

        sat_images_coll = ee.ImageCollection(sat_name)

        # Apply bound filter
        # Select images dates
        # Filter landsat image collection by cloud cover
        # Apply cloud masking
        # Apply the scaling factor function on the set of image collection.
        return sat_images_coll.filterBounds(self._study_region) \
                              .map(lambda image: image.clip(self._study_region)) \
                              .filterDate(self._start_date, self._end_date) \
                              .filter(ee.Filter.lessThan('CLOUD_COVER', 50)) \
                              .map(self._maskSrClouds) \
                              .map(lambda image: self._applyScaleFactors(image, opticalBandsName, thermalBandsName))

    def merge_2images_coll(self, landsat8_images, landsat7_images, merge_bands_names):
        '''
        merge two landsat images using specific bands 

        '''

        self._marged_images = landsat7_images.merge(landsat8_images.select(merge_bands_names)) \
            .map(lambda img: img.toFloat())

        return


class NDVI_Landsat_Detector(Landsat_Analyser):
    '''
    NDVI_Landsat_Detector: calculate Normalized Difference Vegetation Index (NDVI) Layer
    '''

    def get_NDVI(self, visParams={}):
        '''
        visParams :visualization settings
        '''

        self._marged_images = self._marged_images.median()

        # perform normalized difference on red and near infrared bands
        ndvi = self._marged_images.normalizedDifference(['SR_B5', 'SR_B4'])

        map_id_dict = ndvi.getMapId(visParams)

        return ndvi, map_id_dict['tile_fetcher'].url_format


class BAI_Landsat_Detector(Landsat_Analyser):
    '''
    BAI_Landsat_Detector: calculate burn area index (BAI) layer
    '''

    def get_BAI(self, visParams={}):
        '''
        visParams :visualization settings
        '''

        self._marged_images = self._marged_images.median()

        # apply BAI expression on red and near infrared bands
        bai = self._marged_images.expression('1.0 / ((0.1 - RED)**2 + (0.06 - NIR)**2)',
                                             {'NIR': self._marged_images.select('SR_B5'),
                                              'RED': self._marged_images.select('SR_B4'), })

        map_id_dict = bai.getMapId(visParams)

        return bai, map_id_dict['tile_fetcher'].url_format


class Change_Detector:
    '''
    detect changes in vegetation
    '''

    def __init__(self, first_start_date, first_end_date, second_start_date, second_end_date, study_region):
        '''
        class constractor contain 2 landsat analysers
        '''

        self.__first_landsat_analyser = Landsat_Analyser(
            first_start_date, first_end_date, study_region)
        self.__second_landsat_analyser = Landsat_Analyser(
            second_start_date, second_end_date, study_region)

    def __cal_images_per_date(self, sat_name: str, opticalBandsName: str, thermalBandsName: str):
        '''
        get the processed image in every time period
        '''

        first_image = self.__first_landsat_analyser.get_ScFiltMasked_imageColl(sat_name, opticalBandsName, thermalBandsName)  \
                                                   .median()

        second_image = self.__second_landsat_analyser.get_ScFiltMasked_imageColl(sat_name, opticalBandsName, thermalBandsName)  \
                                                     .median()

        return first_image, second_image

    def get_change_detection(self, sat_name,
                             opticalBandsName: str, thermalBandsName: str,
                             visParams={}):
        '''
        calculate change detection layer 
        sat_name: satelite name
        opticalBandsName: optical bands name
        thermalBandsName: thermal bands name
        visParams :visualization settings
        '''

        landsat8_image1, landsat8_image2 = self.__cal_images_per_date(
            sat_name, opticalBandsName, thermalBandsName)

        diff = landsat8_image2.subtract(landsat8_image1)

        magnitude = diff.pow(2)  \
                        .reduce(ee.Reducer.sum().unweighted())  \
                        .sqrt()  \
                        .rename('magnitude')

        angle = diff.select('SR_B4')  \
                    .atan2(diff.select('SR_B5'))  \
                    .multiply(180)  \
                    .divide(math.pi)  \
                    .rename('angle')

        angleReclass = ee.Image(1) \
                         .where(angle.gt(0).And(angle.lte(90)), 1)  \
                         .where(angle.gt(90).And(angle.lte(180)), 2)  \
                         .where(angle.gt(-180).And(angle.lte(-90)), 3)  \
                         .where(angle.gt(-90).And(angle.lte(0)), 4)
        angleReclass = angleReclass.updateMask(magnitude.gte(0.06))

        map_id_dict = angleReclass.getMapId(visParams)

        return angleReclass, map_id_dict['tile_fetcher'].url_format


class TimeSeries_Landsat_Detector(Landsat_Analyser):

    def __AddBandsVariables(self, image):

        imgScaled = image.addBands(image, None, True)
        date = ee.Date(image.get('system:time_start'))
        years = date.difference(ee.Date('1970-01-01'), 'year')

        # add Bands( Add an NDVI band,Add a time band,Add a constant band)
        imgScaled = imgScaled.addBands(imgScaled.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')) \
                             .addBands(ee.Image(years).rename('t')) \
                             .float() \
                             .addBands(ee.Image.constant(1))

        # Return the image with the added bands.
        return imgScaled

    def __AddRadianSinCosBands(self, image):

        timeRadians = image.select('t').multiply(2 * math.pi)

        return image.addBands(timeRadians.cos().rename('cos'))  \
                    .addBands(timeRadians.sin().rename('sin'))

    def get_ScFiltMasked_imageColl(self, sat_name: str, opticalBandsName: str, thermalBandsName: str):
        '''
        get sat_name image collection
        Apply bound filter
        Select images dates
        Apply cloud masking
        Apply the scaling factor function on the set of image collection.
        '''

        sat_images_coll = ee.ImageCollection(sat_name)

        # Apply bound filter
        # Select images dates
        # Apply cloud masking
        # Apply the scaling factor function on the set of image collection.
        return sat_images_coll.filterBounds(self._study_region) \
            .map(lambda image: image.clip(self._study_region)) \
            .filterDate(self._start_date, self._end_date) \
            .map(super(TimeSeries_Landsat_Detector, self)._maskSrClouds) \
            .map(lambda image: super(TimeSeries_Landsat_Detector, self)._applyScaleFactors(image, opticalBandsName, thermalBandsName)) \
            .map(self.__AddBandsVariables)

    def get_TimeSeries_image(self, landsat8sr, visParams={}):

        dependent = ee.String('NDVI')
        harmonicIndependents = ee.List(['constant', 't', 'cos', 'sin'])

        # Add harmonic terms as new image bands.
        harmonicLandsat = landsat8sr.map(self.__AddRadianSinCosBands)

        # Fit the model.
        harmonicTrend = harmonicLandsat.select(harmonicIndependents.add(dependent)) \
                                       .reduce(ee.Reducer.linearRegression(harmonicIndependents.length(), 1))  # The output of this reducer is a 4x1 array image.

        harmonicTrendCoefficients = harmonicTrend.select('coefficients') \
                                                 .arrayProject([0]) \
                                                 .arrayFlatten([harmonicIndependents])

        # Compute fitted values.
        fittedHarmonic = harmonicLandsat.map(lambda image: image.addBands(image.select(harmonicIndependents)
                                                                          .multiply(harmonicTrendCoefficients)
                                                                               .reduce('sum')
                                                                               .rename('fitted')))

        phase = harmonicTrendCoefficients.select('sin') \
                                         .atan2(harmonicTrendCoefficients.select('cos')) \
                                         .unitScale(-math.pi, math.pi)  # Scale to [0, 1] from radians.

        amplitude = harmonicTrendCoefficients.select('sin') \
                                             .hypot(harmonicTrendCoefficients.select('cos')) \
                                             .multiply(5)  # Add a scale factor for visualization.

        # Compute the mean NDVI.
        meanNdvi = landsat8sr.select('NDVI').mean()

        # Use the HSV to RGB transformation to display phase and amplitude.
        rgb = ee.Image.cat([phase,  # hue
                            amplitude,  # saturation (difference from white)
                            meanNdvi  # value (difference from black)
                            ]).hsvToRgb()

        map_id_dict = rgb.getMapId(visParams)

        return rgb, map_id_dict['tile_fetcher'].url_format
