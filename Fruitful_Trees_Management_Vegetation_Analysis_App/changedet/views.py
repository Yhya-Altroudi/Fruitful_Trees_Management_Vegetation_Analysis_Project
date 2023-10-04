import json
from django.shortcuts import render
from django.conf import settings
from django.views.generic import TemplateView
from django.conf import settings
from django.http import HttpResponse
import ee
from .changeDetectionAlgorithms import NDVI_Landsat_Detector
from .changeDetectionAlgorithms import BAI_Landsat_Detector
from .changeDetectionAlgorithms import Change_Detector
from .changeDetectionAlgorithms import TimeSeries_Landsat_Detector
from changedet.changeDetectionSettings import NDVI_SETTINGS, BAI_SETTINGS, CHANGE_DETECTION_SETTINGS, TIME_SERIES_SETTINGS
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views import View
import status
from django.urls import reverse_lazy
from changedet.forms import OnePeriodForm, TwoPeriodsForm
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

# NDVI algorithm view
class NDVI_View(LoginRequiredMixin, View):

    # Get NDVI Page
    def get(self, request) -> render:

        # get form action url
        form_action_url = reverse_lazy('changedet:NDVI_view')

        # add it to template context and return it
        form = OnePeriodForm()

        context = {'action_url': form_action_url, 'form': form}

        return render(request, template_name="changeDet/map.html", context=context)


# Take user input and return NDVI algorithm results


    def post(self, request) -> JsonResponse:

        # load request data as json data
        data = json.loads(request.body)

        form = OnePeriodForm(data)

        if form.is_valid():

            # take user input
            start_date = data.get("start_date", None)
            end_date = data.get("end_date", None)
            polygon_string = data.get("study_region", None)

            # try to convert polygon_string into json format
            try:
                polygon = json.loads(polygon_string)

            except ValueError as e:
                return Response(
                    {"polygon string can not converted into json format": str(
                        e)},
                    status=status.HTTP_400_BAD_REQUEST)

            # Apply NDVI algorithm

            # Create study region
            study_region = ee.Geometry.Polygon(polygon, None, False)

            # Create NDVI land sat detector object
            ndvi = NDVI_Landsat_Detector(start_date, end_date, study_region)

            # get clean landsat8 image collections
            landsat8FiltMasked = ndvi.get_ScFiltMasked_imageColl(sat_name=NDVI_SETTINGS.LANDSAT8_NAME.value,
                                                                 opticalBandsName=NDVI_SETTINGS.L8_OPTICAL_BANDS_NAME.value,
                                                                 thermalBandsName=NDVI_SETTINGS.L8_THERMAL_BANDS_NAME.value)

            # get clean landsat7 image collections and rename bands to be compatible
            landsat7FiltMasked = ndvi.get_ScFiltMasked_imageColl(sat_name=NDVI_SETTINGS.LANDSAT7_NAME.value,
                                                                 opticalBandsName=NDVI_SETTINGS.L7_OPTICAL_BANDS_NAME.value,
                                                                 thermalBandsName=NDVI_SETTINGS.L7_THERMAL_BANDS_NAME.value)

            landsat7FiltMasked = ndvi.rename(landsat7FiltMasked,
                                             old_name=NDVI_SETTINGS.LANDSAT7_OLD_NAME.value,
                                             new_name=NDVI_SETTINGS.LANDSAT7_NEW_NAME.value)

            # merge landsat7 and landsat8 and apply the algorithm
            ndvi.merge_2images_coll(landsat8FiltMasked, landsat7FiltMasked,
                                    merge_bands_names=NDVI_SETTINGS.MERGE_BANDS_NAMES.value)

            # try to implement the algorithm
            try:
                # return the resultls as url
                _, url = ndvi.get_NDVI(NDVI_SETTINGS.VIS_PARAMS.value)

            except ee.ee_exception.EEException as e:
                # return no image error
                return JsonResponse({"url": "", "errors": [GetNoImageErrorMessage()]})
            else:
                return JsonResponse({"url": url})

        else:

            return JsonResponse({"url": "", "errors": GetFormErrorsList(form)})


# BAI algorithm view
class BAI_View(LoginRequiredMixin, View):

    # Get BAI Page
    def get(self, request) -> render:

        # get form action url
        form_action_url = reverse_lazy('changedet:BAI_view')

        # add it to template context and return it
        form = OnePeriodForm()

        context = {'action_url': form_action_url, 'form': form}
        return render(request, template_name="changeDet/map.html", context=context)

    # Take user input and return BAI algorithm results
    def post(self, request) -> JsonResponse:

        # load request data as json data
        data = json.loads(request.body)

        form = OnePeriodForm(data)

        if form.is_valid():
            # take user input
            start_date = data.get("start_date", None)
            end_date = data.get("end_date", None)
            polygon_string = data.get("study_region", None)

            # try to convert polygon_string into json format

            try:
                polygon = json.loads(polygon_string)

            except ValueError as e:
                return Response(
                    {"polygon string can not converted into json format": str(
                        e)},
                    status=status.HTTP_400_BAD_REQUEST)

            # Apply BAI algorithm

            # Create study region
            study_region = ee.Geometry.Polygon(polygon, None, False)

            # Create BAI landsat detector object
            bai = BAI_Landsat_Detector(start_date, end_date, study_region)

            # get clean landsat8 image collections
            landsat8FiltMasked = bai.get_ScFiltMasked_imageColl(sat_name=BAI_SETTINGS.LANDSAT8_NAME.value,
                                                                opticalBandsName=BAI_SETTINGS.L8_OPTICAL_BANDS_NAME.value,
                                                                thermalBandsName=BAI_SETTINGS.L8_THERMAL_BANDS_NAME.value)

            # merge landsat7 and landsat8 and apply the algorithm
            landsat7FiltMasked = bai.get_ScFiltMasked_imageColl(sat_name=BAI_SETTINGS.LANDSAT7_NAME.value,
                                                                opticalBandsName=BAI_SETTINGS.L7_OPTICAL_BANDS_NAME.value,
                                                                thermalBandsName=BAI_SETTINGS.L7_THERMAL_BANDS_NAME.value)
            landsat7FiltMasked = bai.rename(landsat7FiltMasked,
                                            old_name=BAI_SETTINGS.LANDSAT7_OLD_NAME.value,
                                            new_name=BAI_SETTINGS.LANDSAT7_NEW_NAME.value)

            # merge landsat7 and landsat8 and apply the algorithm
            bai.merge_2images_coll(landsat8FiltMasked, landsat7FiltMasked,
                                   merge_bands_names=BAI_SETTINGS.MERGE_BANDS_NAMES.value)

            # try to implement the algorithm
            try:
                # return the resultls as url
                _, url = bai.get_BAI(BAI_SETTINGS.VIS_PARAMS.value)

            except ee.ee_exception.EEException as e:
                # return no image error
                return JsonResponse({"url": "", "errors": [GetNoImageErrorMessage()]})
            else:
                return JsonResponse({"url": url})

        else:
            return JsonResponse({"url": "", "errors": GetFormErrorsList(form)})


class Change_Det_View(LoginRequiredMixin, View):

    def get(self, request) -> render:
        # get form action url
        form_action_url = reverse_lazy('changedet:ChangeDet_view')

        # add it to template context and return it
        form = TwoPeriodsForm()

        context = {'action_url': form_action_url, 'form': form}

        return render(request, template_name="changeDet/map.html", context=context)

    def post(self, request) -> JsonResponse:

        # load request data as json data
        data = json.loads(request.body)

        form = TwoPeriodsForm(data)

        if form.is_valid():

            # take user input
            first_start_date = data.get("first_start_date", None)
            first_end_date = data.get("first_end_date", None)

            second_start_date = data.get("second_start_date", None)
            second_end_date = data.get("second_end_date", None)

            polygon_string = data.get("study_region", None)

            # try to convert polygon_string into json format
            try:
                polygon = json.loads(polygon_string)

            except ValueError as e:
                return Response(
                    {"polygon string can not converted into json format": str(
                        e)},
                    status=status.HTTP_400_BAD_REQUEST)

            # Apply Change Detection algorithm algorithm

            # Create study region
            study_region = ee.Geometry.Polygon(polygon, None, False)

            # create change_detector object
            change_detector = Change_Detector(first_start_date, first_end_date,
                                              second_start_date, second_end_date,
                                              study_region)

            # try to implement the algorithm
            try:
                # apply change detection algorithm
                _, url = change_detector.get_change_detection(CHANGE_DETECTION_SETTINGS.LANDSAT8_NAME.value,
                                                              CHANGE_DETECTION_SETTINGS.L8_OPTICAL_BANDS_NAME.value,
                                                              CHANGE_DETECTION_SETTINGS.L8_THERMAL_BANDS_NAME.value,
                                                              CHANGE_DETECTION_SETTINGS.VIS_PARAMS.value)

            # try to implement the algorithm
            except ee.ee_exception.EEException as e:

                # return no image error
                return JsonResponse({"url": "", "errors": [GetNoImageErrorMessage()]})
            else:
                return JsonResponse({"url": url})

        else:
            return JsonResponse({"url": "", "errors": GetFormErrorsList(form)})


class Time_Series_view(LoginRequiredMixin, View):

    def get(self, request) -> render:

        # get form action url
        form_action_url = reverse_lazy('changedet:TimeSeries_view')

        # add it to template context and return it
        form = OnePeriodForm()

        context = {'action_url': form_action_url, 'form': form}

        return render(request, template_name="changeDet/map.html", context=context)

    def post(self, request) -> JsonResponse:

        # load request data as json data
        data = json.loads(request.body)

        form = OnePeriodForm(data)

        if form.is_valid():

            # take user input
            start_date = data.get("start_date", None)
            end_date = data.get("end_date", None)
            polygon_string = data.get("study_region", None)

            # try to convert polygon_string into json format
            try:
                polygon = json.loads(polygon_string)

            except ValueError as e:
                return Response(
                    {"polygon string can not converted into json format": str(
                        e)},
                    status=status.HTTP_400_BAD_REQUEST)

            # Create study region
            study_region = ee.Geometry.Polygon(polygon, None, False)

            # Apply Timeseries algorithm

            timeSeries = TimeSeries_Landsat_Detector(
                start_date, end_date, study_region)

            # get clean landsat8 image collections
            landsat8sr = timeSeries.get_ScFiltMasked_imageColl(sat_name=TIME_SERIES_SETTINGS.LANDSAT8_NAME.value,
                                                               opticalBandsName=TIME_SERIES_SETTINGS.L8_OPTICAL_BANDS_NAME.value,
                                                               thermalBandsName=TIME_SERIES_SETTINGS.L8_THERMAL_BANDS_NAME.value)

            # try to implement the algorithm
            try:
                # apply change detection algorithm
                _, url = timeSeries.get_TimeSeries_image(landsat8sr=landsat8sr,
                                                         visParams=TIME_SERIES_SETTINGS.VIS_PARAMS.value)
            except ee.ee_exception.EEException as e:

                # return no image error
                return JsonResponse({"url": "", "errors": [GetNoImageErrorMessage()]})
            else:
                return JsonResponse({"url": url})

        else:
            return JsonResponse({"url": "", "errors": GetFormErrorsList(form)})


def test(request):

    if request.method == "POST":
        form = OnePeriodForm(request.POST)
        print(request.POST)
        # if form.is_valid():
        #    print('The form is valid')
        # else:
        #    print(form.errors)

    else:
        # add it to template context and return it
        form = OnePeriodForm()

    url = reverse_lazy('changedet:testing_url')

    context = {'form': form, 'action_url': url}

    return render(request, 'changeDet/changDetBase.html')


# Functions
def GetFormErrorsList(form):

    errors = []

    for valid in form.errors.as_data()['__all__']:
        errors.append(valid.message)

    return errors


def GetNoImageErrorMessage():
    return "There is no image in ranges and location that you selected"
