# -*- coding: utf-8 -*-

import arcpy
import yaml
from os.path import join, dirname, abspath

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
            parameterType='Optional',
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
            parameterType='Required',
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
            for item in range(2, len(parameters)-1):
                parameters[item].enabled = False
        else:
            for item in range(2, len(parameters)-1):
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

    def addPayloadItem(self, parameters, feature):
        """getting field names"""
        location_name = parameters[2].valueAsText
        address_name = parameters[3].valueAsText
        city_name = parameters[4].valueAsText
        zip_code = parameters[5].valueAsText
        region_name = parameters[6].valueAsText
        country = parameters[7].valueAsText
        geometry = parameters[1].valueAsText
        item = {
            "query_id": 1,
        }
        if location_name != "":
            item["location_name"] = self.valueCheck(
                str(feature.getValue(location_name)))
        if address_name != "":
            item["street_address"] = self.valueCheck(str(feature.getValue(address_name)))
        if city_name != "":
            item["city"] = self.valueCheck(str(feature.getValue(city_name)))
        if zip_code != "":
            item["postal_code"] = self.valueCheck(str(feature.getValue(zip_code)))
        if region_name != "":
            item["region"] = self.valueCheck(str(feature.getValue(region_name)))
        if country != "":
            item["iso_country_code"] = self.valueCheck(str(feature.getValue(country)))
        if country == "":
            item["iso_country_code"] = "US"

        ManageKey.logInfo(self, "{}".format(item), 1)
            #featGeometry = feature.geometry().centroid()
            #sourceCrs = source.sourceCrs()
            #if source.sourceCrs != QgsCoordinateReferenceSystem(4326):
            #    destCrs = QgsCoordinateReferenceSystem(4326)
            #    tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            #    featGeometry.transform(tr)
            #if math.isnan(featGeometry.asPoint().y()) is False:
            #    item["latitude"] = featGeometry.asPoint().y()
            #    item["longitude"] = featGeometry.asPoint().x()
            #else:
             #   print("strange geometry found at feature with id " + str(feature.id()))
        return item

    def execute(self, parameters, messages):
        """The source code of the tool."""
        key = self.get_config()
        ManageKey.logInfo(self, "API Key used: " + key, 1)
        # getting the input values:
        in_fc = parameters[0].value
        #location = parameters[1].valueAsText
        #address = parameters[2].valueAsText
        #city = parameters[3].valueAsText
        #postal = parameters[4].valueAsText
        #region = parameters[5].valueAsText
        country = parameters[7].valueAsText
        #ManageKey.logInfo(self, "Feature {}:".format(type(region)), 1)

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

        for row in arcpy.da.SearchCursor(in_fc, ['*']):
            # Print the current multipoint's ID
            ManageKey.logInfo(self, "Feature {}:".format(row), 1)
            index += 1
            if index % 100 != 0 and index != count:
                payloadItem = self.addPayloadItem(parameters,
                                                  row)
                payload["queries"].append(payloadItem)
            if index % 100 == 0:
                payloadItem = self.addPayloadItem(parameters,
                                                  row)
                payload["queries"].append(payloadItem)
                batches.append(payload)
                payload = {"queries": []}
            if index == count:
                payloadItem = self.addPayloadItem(parameters,
                                                  row)
                payload["queries"].append(payloadItem)
                batches.append(payload)
                payload = {"queries": []}

        return
