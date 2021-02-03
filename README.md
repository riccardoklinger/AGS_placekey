# Placekey API Toolbox for ArcGIS Pro

IMPORTANT NOTE: Currently only fully supported for US-based Addresses and POIs.

Placekey is designed to be a free, universal identifier for physical places. The Placekey API does the work of POI resolution, address normalization, validation, and geocoding to ensure that unique places receive unique Placekeys. Learn more at placekey.io.

With the Placekey Toolbox for ArcGIS Pro 2.7+ you can process different layers/files and get the Placekey for each feature using the Placekey API.

![Toolbox](https://i.imgur.com/s6W0aQE.png)

Use this Plugin to perform the following:
## Address and POI Matching

If you are drawing address and/or POI-oriented data from multiple different places, Placekey allows you to match them together easily. Placekey can act as an alternative to a spatial join, letting you join on the Placekey attribute. This significantly reduces the downsides of spatial joins - these include geocodes on top of each other in apartment buildings or offices, densely-placed geocodes in urban areas, and street-level versus rooftop-level geocodings.
## Address Normalization

By resolving messy input address formats, Placekey removes the need to first normalize your addresses and POIs when joining them with other data. The Placekey API ensures that the same place will receive the same Placekey, even if it is referenced using multiple names and/or address conventions.
## Address and POI Deduplication

Placekey can help you remove duplicate rows in your dataset, even if their address and POI formats differ. Just Placekey all of your rows and drop duplicates of the Placekey attribute.
## Evaluate Address Data Quality

The Placekey API compares your address and POI data against multiple authoritative sources of truth in order to generate a unique Placekey for each place in your dataset. Overall data quality can be ascertained by appending Placekeys and looking at the match rate.

## Prerequesities

Please get yourself a Placekey API key at [placekey.io](https://placekey.io). Then use the processing step "Add/Change API key" to save your API key to a local file (params.yaml) for later usage.

## Install

Please download the toolbox and install it using the Catalog by adding a toolbox:

![Adding a toolbox](https://i.imgur.com/1xHoCOE.gif)

## Usage

Currently, vector layers and Geodatabase Tables are supported. If no latitude and longitude is available in your layer, make sure to fill the attributes:
    
    DIALOG ATTRIBUTE        | TECHNICAL     | DESCRIPTION
    Input Features          | in_features   | the layer/table with input features
    Geometry information    | geometryInfo  | whether or not to use geometry information
    Location Name Field     | location      | the name of the place / location 
    Address Field           | address       | street name + house number
    City Name Field         | city          | The city name
    Postal Code Field       | postal        | the zip code
    Region Name Field       | region        | region / state 
    ISO Country Field       | country       | only US and NL are supported right now If no country is provided, the plugin defaults it to US.
    Output                  | out_features  | The layer/Table contianing the result

The API supports various sub-combinations of the above attributes, such as (location_name, latitude, and longitude), (street_address, city, and region), (street_address, region, and postal_code). For full API specifications, please see the API docs.

If you would like to drop the geometry information, select "USE Attributes for WHERE-part" in the dialog. 

![Dialog with all parameters](https://i.imgur.com/80DrT8a.png)
*Dialog with all parameters*

Otherwise we will use point-geometries. If your layer is of type polygon/polyline, we will calculate centroids and use them as inputs for latitude and longitude. This will be treated as prime information on the API side, so will outrule the attribute information (like street_address, postal_code and so on).

![Dialog for simple Input using geometries](https://i.imgur.com/C8oyiMy.png)
*Dialog for simple Input using geometries*

Resulting Layer will use EPSG 4326 and the centroids of input data if available.
