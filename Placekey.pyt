# -*- coding: utf-8 -*-

import arcpy
import yaml
import math
import json
import requests
import time
from os.path import join, dirname, abspath
import numpy as np

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Placekey Toolbox"
        self.alias = "PlacekeyToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [ManageKey, AddPlacekeys]


class ManageKey(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add/Change API Key"
        self.description = "Add or change the API Key in a local parameter file for use with the API"
        self.canRunInBackground = False

    def logInfo(self, msg, loglevel):
        logfile = join(dirname(abspath(__file__)), 'log.log')
        if loglevel == 1:
            log = open(logfile, 'a')
            log.write('\nINFO\t')
            log.write(msg)
            log.close()
            arcpy.AddMessage(msg)
        if loglevel == 2:
            log = open(logfile, 'a')
            log.write('\nWARN\t')
            log.write(msg)
            log.close()
            arcpy.AddWarning(msg)
        if loglevel == 3:
            log = open(logfile, 'a')
            log.write('\nERRR\t')
            log.write(msg)
            log.close()
            arcpy.AddError(msg)
        return

    def getParameterInfo(self):
        """Define parameter definitions"""
        in_key = arcpy.Parameter(
                name='API_key',
                displayName='API Key',
                datatype='GPString',
                direction='Input',
                parameterType='Required')
        with open(join(dirname(abspath(__file__)), 'params.yaml'), 'r') as f:
            try:
                config = yaml.load(f, Loader=yaml.FullLoader)
                key = config["apiKey"]
                in_key.value = key
            except yaml.YAMLError as exc:
                self.logInfo(str(exc), 1)
        return [in_key]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        self.logInfo("old Api Key was " + parameters[0].value, 1)
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        dict_file = {'apiKey': parameters[0].value}

        with open(join(dirname(abspath(__file__)), 'params.yaml'), 'w') as file:
            documents = yaml.dump(dict_file, file)
        self.logInfo("new Api Key is " + parameters[0].value, 1)
        return


class AddPlacekeys(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add Placekeys to features"
        self.description = "Get Placekeys for POIs"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            name='in_features',
            displayName='Input Features',
            datatype='GPFeatureLayer',
            direction='Input',
            parameterType='Required')
        param1 = arcpy.Parameter(
            displayName="Geometry information",
            name="geometryInfo",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Use Geometry for WHERE-part", "Use Attributes for WHERE-part"]
        param1.value = "Use Geometry for WHERE-part"
        param2 = arcpy.Parameter(
            displayName='Location Name Field',
            name='location',
            datatype='Field',
            parameterType='Required',
            direction='Input')
        param2.parameterDependencies = [param0.name]
        param3 = arcpy.Parameter(
            displayName='Address Field',
            name='address',
            datatype='Field',
            parameterType='Optional',
            direction='Input')
        param3.parameterDependencies = [param0.name]
        param4 = arcpy.Parameter(
            displayName='City Name Field',
            name='city',
            datatype='Field',
            parameterType='Optional',
            direction='Input')
        param4.parameterDependencies = [param0.name]
        param5 = arcpy.Parameter(
            displayName='Postal Code Field',
            name='postal',
            datatype='Field',
            parameterType='Optional',
            direction='Input')
        param5.parameterDependencies = [param0.name]
        param6 = arcpy.Parameter(
            displayName='Region Name Field',
            name='region',
            datatype='Field',
            parameterType='Optional',
            direction='Input')
        param6.parameterDependencies = [param0.name]
        param7 = arcpy.Parameter(
            displayName='ISO Country Field',
            name='country',
            datatype='Field',
            parameterType='Optional',
            direction='Input')
        param7.parameterDependencies = [param0.name]
        param8 = arcpy.Parameter(
            displayName="Output",
            name="out_features",
            datatype="GPFeatureLayer",
            direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[1].value == "Use Geometry for WHERE-part":
            for item in range(3, len(parameters)-1):
                parameters[item].enabled = False
        else:
            for item in range(3, len(parameters)-1):
                parameters[item].enabled = True

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return


    def get_config(self):
        """Load the configuration file and find either major OSM tag keys or
        suitable OSM tag values for a given key"""
        # Load yaml file with configuration info
        with open(join(dirname(abspath(__file__)), 'params.yaml'), 'r') as f:
            try:
                config = yaml.load(f, Loader=yaml.FullLoader)
                key = config["apiKey"]
            except yaml.YAMLError as exc:
                ManageKey.logInfo(self, str(exc), 3)
        return key

    def valueCheck(self, string):
        if string == "nan" or string == "NULL" or string == "0":
            return ""
        else:
            return string

    def addPayloadItem(self, parameters, feature, fields):
        """getting field names"""
        location_name = parameters[2].valueAsText
        address_name = parameters[3].valueAsText
        city_name = parameters[4].valueAsText
        zip_code = parameters[5].valueAsText
        region_name = parameters[6].valueAsText
        country = parameters[7].valueAsText
        geometry = parameters[1].valueAsText
        item = {
            "query_id": str(feature[-1])
        }
        if location_name != "" and location_name is not None:
            item["location_name"] = self.valueCheck(
                str(feature[fields.index(location_name)]))
        if address_name != "" and address_name is not None:
            item["street_address"] = self.valueCheck(str(feature[fields.index(address_name)]))
        if city_name != "" and city_name is not None:
            item["city"] = self.valueCheck(str(feature[fields.index(city_name)]))
        if zip_code != "" and zip_code is not None:
            #ManageKey.logInfo(self, "{}".format(type(zip_code), 3)
            item["postal_code"] = self.valueCheck(str(feature[fields.index(zip_code)]))
        if region_name != "" and region_name is not None:
            item["region"] = self.valueCheck(str(feature[fields.index(region_name)]))
        if country != "" and country is not None:
            item["iso_country_code"] = self.valueCheck(str(feature[fields.index(country)]))
        if country == "" or country is None:
            item["iso_country_code"] = "US"
        if geometry == "Use Geometry for WHERE-part":
            try:
                geom = feature[fields.index("SHAPE@")]
                ManageKey.logInfo(self, "{}".format(type(geom)), 1)
                spatial_ref = arcpy.Describe(parameters[0].value).spatialReference
                if spatial_ref.factoryCode != "4326":
                    #X, Y = geom.centroid.X, geom.centroid.Y
                    srOUT = arcpy.SpatialReference(4326)  # GCS_WGS84
                    geom2 = geom.projectAs(srOUT)
                    X, Y = geom2.centroid.X, geom2.centroid.Y
                else:
                    X, Y = geom.centroid.X, geom.centroid.Y
                if math.isnan(X) is False:
                    item["latitude"] = Y
                    item["longitude"] = X
                else:
                    ManageKey.logInfo(self, "Strange geometry found at feature with id " + str(feature[7]),2)
            except:
                ManageKey.logInfo(self, "Strange geometry found at feature with id " + str(feature[7]), 2)

        ManageKey.logInfo(self, "{}".format(item), 1)
        return item

    def getKeys(self, payload, result, key):
        url = "https://api.placekey.io/v1/placekeys"
        headers = {
            'apikey': key,
            'Content-Type': 'application/json',
            'user-agent': 'placekey-arcGIS/0.8 batchMode'
        }
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=json.dumps(payload)
        )
        if response.status_code == 401:
            ManageKey.logInfo(self, "check your API key. Seems like you're unauthorized!", 2)
            ManageKey.logInfo(self, "invalid API key", 3)
        if response.status_code == 429:
            for retry in range(1, 11):
                ManageKey.logInfo(self, 'waiting 10s, rate limit exceeded', 2)
                ManageKey.logInfo(self, "trying again" + str(retry) + "/10 ", 2)
                time.sleep(10)
                response = requests.request(
                    "POST",
                    url,
                    headers=headers,
                    data=json.dumps(payload)
                )
                if response.status_code == 200:
                    break
                if retry == 10:
                    ManageKey.logInfo(self, "tried 10 times, cancelling processing", 3)
        if response.status_code == 200:
            if "error" in response.json():
                for entry in payload["queries"]:
                    result.append(json.loads(
                        """{"query_id": """ +
                        str(entry["query_id"]) +
                        """, "placekey": "Invalid address"}"""))
            else:
                for item in response.json():
                    if "placekey" in item:
                        result.append(item)
                    if "error" in item:
                        result.append(json.loads(
                            """{"query_id": """ +
                            str(item["query_id"]) +
                            """, "placekey": "Invalid address"}"""))
        if response.status_code == 400:
            try:
                if response.json()["error"][0:2] == "All":
                    for entry in payload["queries"]:
                        result.append(json.loads(
                            """{"query_id": """ +
                            str(entry["query_id"]) +
                            """, "placekey": "Invalid address"}"""))
            except BaseException:
                ManageKey.logInfo(self,
                    """No proper request sent. Details in the python log,
                    make sure to have a proper set off attributes.
                    If you're using a point layer, make sure to have
                    valid geometries for all features! Response was: """ +
                    response.text,
                    3
                )

        return result

    def execute(self, parameters, messages):
        """The source code of the tool."""
        key = self.get_config()
        ManageKey.logInfo(self, "API Key used: " + key, 1)
        # getting the input values:
        in_fc = parameters[0].value
        # getting fields:
        fields = []

        for item in range(2,len(parameters)-1):
            if parameters[item].valueAsText:
                fields.append(parameters[item].valueAsText)
        fields.append("SHAPE@")
        #adding object ID
        oidfield = arcpy.Describe(parameters[0].value).OIDFieldName
        fields.append(oidfield)
        ManageKey.logInfo(self, "items {}:".format(fields), 1)
        country = parameters[7].valueAsText
        #holding the batch info:
        payload = {"queries": []}
        batches = []
        result = []

        if country is None:
            # default to "US"
            ManageKey.logInfo(self, "no country specified, using 'US' for all features", 2)
        # reading the in_fc:
        index = 0
        # number of features:
        arcpy.MakeTableView_management(in_fc, "in_memory_view")
        count = int(arcpy.GetCount_management("in_memory_view").getOutput(0))
        for row in arcpy.da.SearchCursor(in_fc, fields):
            # Print the current multipoint's ID
            ManageKey.logInfo(self, "Feature: {}".format(row), 1)
            index += 1
            if index % 100 != 0 and index != count:
                payloadItem = self.addPayloadItem(parameters,
                                                  row,
                                                  fields)
                payload["queries"].append(payloadItem)
            if index % 100 == 0:
                payloadItem = self.addPayloadItem(parameters,
                                                  row,
                                                  fields)
                payload["queries"].append(payloadItem)
                batches.append(payload)
                payload = {"queries": []}
            if index == count:
                payloadItem = self.addPayloadItem(parameters,
                                                  row,
                                                  fields)
                payload["queries"].append(payloadItem)
                batches.append(payload)
                payload = {"queries": []}
        current_batch = 0
        batch_count = len(batches)
        arcpy.SetProgressor("step", "Copying shapefiles to geodatabase...",
                            0, batch_count, 1)
        for batch in batches:
            current_batch += 1
            result = self.getKeys(batch, result, key)
            arcpy.SetProgressorLabel("working on batch {0} out of {1}".format(batch, batch_count))
            arcpy.SetProgressorPosition()
        arcpy.ResetProgressor()
        arcpy.AddMessage("{}".format(result))
        return
