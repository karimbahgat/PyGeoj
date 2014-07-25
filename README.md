# PyGeoj

**Version: 0.1.0**

**Date: July 25, 2014**

**Author: [Karim Bahgat](https://uit.academia.edu/KarimBahgat)**

**Contact: karim.bahgat.norway@gmail.com**

**Homepage: https://github.com/karimbahgat/pygeoj**

## Table of Content

- [About](#about)
  - [System Compatibility](#system-compatibility)
  - [Dependencies](#dependencies)
  - [License](#license)
- [Basic Usage](#basic-usage)
  - [Setup](#setup)
  - [Reading](#reading)
  - [Editing](#editing)
  - [Constructing](#constructing)
- [Functions and Classes](#functions-and-classes)
  - [pygeoj.Feature](#pygeojfeature----class-object)
    - [.validate](#validate)
  - [pygeoj.GeojsonFile](#pygeojgeojsonfile----class-object)
    - [.add_all_bboxes](#add_all_bboxes)
    - [.add_unique_id](#add_unique_id)
    - [.addfeature](#addfeature)
    - [.define_crs](#define_crs)
    - [.getfeature](#getfeature)
    - [.insertfeature](#insertfeature)
    - [.removefeature](#removefeature)
    - [.replacefeature](#replacefeature)
    - [.save](#save)
    - [.update_bbox](#update_bbox)
  - [pygeoj.Geometry](#pygeojgeometry----class-object)
    - [.validate](#validate)
  - [pygeoj.load](#pygeojload)
  - [pygeoj.new](#pygeojnew)


## About

A simple Python Geojson file reader and writer.

### System Compatibility

Should work on Python version 2.x and Windows. Has not yet been tested on
Python 3.x or other OS systems.

### Dependencies

None.

### License

This code is free to share, use, reuse,
and modify according to the MIT license, see license.txt

## Basic Usage

### Setup

PyGeoj is installed by simply placing the "pygeoj" package folder in an importable location like 
"C:/PythonXX/Lib/site-packages". It can then be imported with:

```
import pygeoj
```

### Reading

Reading geojson formatted GIS files is a simple one-liner (requires the geojson file to be a 

"FeatureCollection", the most sensible format for most GIS files):

```
testfile = pygeoj.load(filepath="testfile.geojson")
```

Basic information about the geojson file can then be extracted, such as:

```
len(testfile) # the number of features
testfile.bbox # the bounding box region of the entire file
testfile.crs # the coordinate reference system
testfile.common_attributes # retrieves which field attributes are common to all features
```

Individual features can be accessed either by their index in the features list:

```
testfile.getfeature(3)
```

Or by iterating through all of them:

```
for feature in testfile: 
    # do something
```

A feature can be inspected in various ways:

```
feature.properties
feature.geometry.coordinates
feature.geometry.bbox
```

### Editing

The standard Python list operations can be used to edit and swap around the features in a geojson 

instance, and then saving to a new geojson file:

```
_third = testfile.getfeature(3)

testfile.insertfeature(8, _third)

testfile.replacefeature(1, _third)

testfile.removefeature(3)

testfile.save("test_edit.geojson")
```

An existing feature can also be tweaked by using simple attribute-setting:

```
# set your own properties
_third.properties = {"newfield1":"newvalue1", "newfield2":"newvalue2"}

# borrow the geometry of the 16th feature
_third.geometry = testfile.getfeature(16).geometry
```

### Constructing

Creating a new geojson file from scratch is also easy:

```
newfile = pygeoj.new()

# The data coordinate system defaults to long/lat WGS84 or can be manually defined:
newfile.define_crs(type="link", link="http://spatialreference.org/ref/epsg/26912/esriwkt/", link_type="esriwkt")
```

The new file can then be populated with custom-made features created with the Feature and Geometry 

classes:

```
_Norwayfeat_ = pygeoj.Feature(properties={"country":"Norway"},
                            geometry=pygeoj.Geometry(type="Polygon", coordinates=[[(21,3),(33,11),(44,22)]]))
_USAfeat_ = pygeoj.Feature(properties={"country":"USA"},
                          geometry=pygeoj.Geometry(type="Polygon", coordinates=[[(11,23),(14,5),(66,31)]]))
newfile.addfeature(_Norwayfeat_)
newfile.addfeature(_USAfeat_)
```

Finally, some useful additional information can be added to top off the geojson file before saving it to 

file:
 
```
newfile.add_all_bboxes()

newfile.add_unique_id()

newfile.save("test_construct.geojson")
```

## Functions and Classes

### pygeoj.Feature(...) --> class object
A feature instance.

| __option__    | __description__ 
| --- | --- 
| obj | another feature instance, an object with the __geo_interface__ or a geojson dictionary of the Feature type
| geometry/properties | if obj isn't specified, geometry and properties can be set as arguments directly, with geometry being anything that the Geometry instance can accept, and properties being an optional dictionary.

Attributes include:

| __attribute__    | __description__ 
| --- | ---
| geometry | a Geometry instance
| properties | a properties dictionary

  - #### .validate(...):
  Validates that the feature is correctly formatted, and raises an error if not

### pygeoj.GeojsonFile(...) --> class object
An instance of a geojson file. Can load from data or from a file,
which can then be read or edited.
Call without any arguments to create an empty geojson file
so you can construct it from scratch.

Note: In order for a geojson dict to be considered a file,
it cannot just be single geometries, so this class always
saves them as the toplevel FeatureCollection type,
and requires the files it loads to be the same.

| __option__    | __description__ 
| --- | --- 
| filepath | the path of a geojson file to load (optional).
| data | a complete geojson dictionary to load (optional).

Has the following attributes:

| __attribute__    | __description__ 
| --- | ---
| crs | The geojson formatted dictionary of the file's coordinate reference system
| bbox | The bounding box surrounding all geometries in the file. You may need to call .update_bbox() to make sure this one is up-to-date.
| common_attributes | Collects and returns a list of attributes/properties/fields common to all features

  - #### .add_all_bboxes(...):
  Calculates and adds a bbox attribute to all feature geometries

  - #### .add_unique_id(...):
  Adds a unique id property to each feature.
  Note: Results in error if any of the features already
  have an "id" field

  - #### .addfeature(...):
  - no documentation for this method

  - #### .define_crs(...):
  Defines the coordinate reference system for the geojson file.
  Note: for link crs, only online urls are supported
  (no auxilliary crs files)
  
  | __option__    | __description__ 
  | --- | --- 
  | type | the type of crs, either "name" or "link"
  | name | the crs name as an OGC formatted crs string (eg "urn:ogc:def:crs:..."), required if type is "name"
  | link | the crs online url link address, required if type is "link"
  | link_type | the type of crs link, optional if type is "link"

  - #### .getfeature(...):
  - no documentation for this method

  - #### .insertfeature(...):
  - no documentation for this method

  - #### .removefeature(...):
  - no documentation for this method

  - #### .replacefeature(...):
  - no documentation for this method

  - #### .save(...):
  Saves the geojson instance to file.
  Note: to save with a different text encoding use the 'encoding' argument.
  
  | __option__    | __description__ 
  | --- | ---
  | savepath | filepath to save the file

  - #### .update_bbox(...):
  Recalculates the bbox region for the entire shapefile.
  Useful after adding and/or removing features.
  Note: No need to use this method just for saving, because saving
  automatically updates the bbox.

### pygeoj.Geometry(...) --> class object
A geometry instance.
Can be created from args, or without any to create an empty one from scratch.

| __option__    | __description__ 
| --- | --- 
| obj | another geometry instance, an object with the __geo_interface__ or a geojson dictionary of the Geometry type
| type/coordinates/bbox | if obj isn't specified, type, coordinates, and optionally bbox can be set as arguments

Has several geometrical attribute values. 

| __attribute__    | __description__ 
| --- | --- 
| type | as specified when constructed
| coordinates | as specified when constructed
| bbox | if bbox wasn't specified when constructed then it is calculated on-the-fly

  - #### .validate(...):
  Validates that the geometry is correctly formatted, and raises an error if not

### pygeoj.load(...):
Loads a geojson file or dictionary, validates it, and returns a
GeojsonFile instance.

Note: In order for a geojson dict to be considered a file,
it cannot just be single geometries, so this class always
saves them as the toplevel FeatureCollection type,
and requires the files it loads to be the same.

Note: to load with a different text encoding use the 'encoding' argument.

| __option__    | __description__ 
| --- | --- 
| filepath | the path of a geojson file to load (optional).
| data | a complete geojson dictionary to load (optional).

### pygeoj.new(...):
Creates and returns a new empty geojson file instance.

