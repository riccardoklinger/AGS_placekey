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
        in_fc = arcpy.Parameter(
            name='in_features',
            displayName='Input Features',
            datatype='GPFeatureLayer',
            direction='Input',
            parameterType='Required')
        paramxy = arcpy.Parameter(
                displayName="Geometry information",
                name="geometryInfo",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        paramxy.filter.list = ["Use Geometry for WHERE-part", "Use Attributes for WHERE-part"]
        paramxy.value = "Use Geometry for WHERE-part"
        param1 = arcpy.Parameter(
            displayName='Location Name Field',
            name='location',
            datatype='Field',
            parameterType='Required',
            direction='Input')
        param1.parameterDependencies = [in_fc.name]
        param2 = arcpy.Parameter(
            displayName='Address Field',
            name='address',
            datatype='Field',
            parameterType='Required',
            direction='Input')
        param2.parameterDependencies = [in_fc.name]
        param3 = arcpy.Parameter(
            displayName='City Name Field',
            name='city',
            datatype='Field',
            parameterType='Required',
            direction='Input')
        param3.parameterDependencies = [in_fc.name]
        param4 = arcpy.Parameter(
            displayName='Postal Code Field',
            name='postal',
            datatype='Field',
            parameterType='Required',
            direction='Input')
        param4.parameterDependencies = [in_fc.name]
        param5 = arcpy.Parameter(
            displayName='Region Name Field',
            name='region',
            datatype='Field',
            parameterType='Required',
            direction='Input')
        param5.parameterDependencies = [in_fc.name]
        param6 = arcpy.Parameter(
            displayName='ISO Country Field',
            name='country',
            datatype='Field',
            parameterType='Optional',
            direction='Input')
        param6.parameterDependencies = [in_fc.name]
        param7 = arcpy.Parameter(
            displayName="Output",
            name="out_features",
            datatype="GPFeatureLayer",
            direction="Output")

        return [in_fc, param1, paramxy, param2, param3, param4, param5, param6, param7, ]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[2].value == "Use Geometry for WHERE-part":
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


    def execute(self, parameters, messages):
        """The source code of the tool."""
        key = self.get_config()
        ManageKey.logInfo(self, "API Key used: " + key, 1)
        # getting the input values:
        in_fc = parameters[0].value
        location = parameters[1].valueAsText
        address = parameters[2].valueAsText
        city = parameters[3].valueAsText
        postal = parameters[4].valueAsText
        region = parameters[5].valueAsText
        country = parameters[6].valueAsText
        ManageKey.logInfo(self, "Feature {}:".format(type(region)), 1)
        if country is None:
            # default to "US"
            ManageKey.logInfo(self, "no country specified, using 'US' for all features", 2)
        # reading the in_fc:
        for row in arcpy.da.SearchCursor(in_fc):
            # Print the current multipoint's ID
            ManageKey.logInfo(self, "Feature {}:".format(row), 1)
        return
