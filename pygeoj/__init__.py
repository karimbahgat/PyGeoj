"""
A simple Python Geojson file reader and writer.
Author: Karim Bahgat, 2014
Contact: karim.bahgat.norway@gmail.com
License: MIT License

## Table of Content
- [Basic Usage](#basic-usage)
  - [setup](#setup)
  - [reading](#reading)
  - [editing](#editing)
  - [constructing](#constructing)

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
newfile.define_crs(type="link", link="http://spatialreference.org/ref/epsg/26912/esriwkt/", 

link_type="esriwkt")
```

The new file can then be populated with custom-made features created with the Feature and Geometry 

classes:

```
_Norwayfeat_ = pygeoj.Feature(properties={"country":"Norway"},
                          geometry=pygeoj.Geometry(type="Polygon", coordinates=[[(21,3),(33,11),

(44,22)]]))
_USAfeat_ = pygeoj.Feature(properties={"country":"USA"},
                          geometry=pygeoj.Geometry(type="Polygon", coordinates=[[(21,3),(33,11),

(44,22)]]))
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
"""

from .main import Geometry, Feature, GeojsonFile
from .main import load, new
