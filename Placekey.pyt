# -*- coding: utf-8 -*-

import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Placekey Toolbox"
        self.alias = "PlacekeyToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [AddPlacekeys]


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
            parameterType='Required',
            direction='Input')
        param6.parameterDependencies = [in_fc.name]
        param7 = arcpy.Parameter(
            displayName="Output",
            name="out_features",
            datatype="GPFeatureLayer",
            direction="Output")

        return [in_fc, param2, param1, param3, param4, param5, param6, param7]

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
        return

    def create_result_fc():
        return

    def get_config(self, config_item):
        """Load the configuration file and find either major OSM tag keys or
        suitable OSM tag values for a given key"""
        # Load JSON file with configuration info
        json_file = join(dirname(abspath(__file__)), 'config/api.json')
        try:
            with open(json_file ) as f:
                config_json = json.load(f)
        except IOError:
            arcpy.AddError('Configuration file %s not found.' % json_file)
        except ValueError:
            arcpy.AddError('Configuration file %s is not valid JSON.' %
                           json_file)
        # Compile a list of all major OSM tag keys
        if config_item == "all":
            return sorted([key for key in config_json])
        # Compile a list of all major OSM tag values for the given OSM tag key
        else:
            return ""


    def execute(self, parameters, messages):
        """The source code of the tool."""
        return
