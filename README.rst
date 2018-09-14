PyGeoj
======

PyGeoj is a simple Python GeoJSON file reader and writer intended for
end-users. It exposees dictionary structures as high level objects with
convenience methods, so the user does not have to get caught up in the
details of the format specification.

Platforms
---------

Python 2 and 3.

Dependencies
------------

Pure Python, no dependencies.

Installing it
-------------

PyGeoj is installed with pip from the commandline:

::

    pip install pygeoj

It also works to just place the "pygeoj" package folder in an importable
location like "PythonXX/Lib/site-packages".

Example Usage
-------------

Begin by importing the pygeoj module:

::

    import pygeoj

Reading
~~~~~~~

Reading geojson formatted GIS files is a simple one-liner (requires the
geojson file to be a "FeatureCollection"):

::

    testfile = pygeoj.load(filepath="testfile.geojson")
    # or
    testfile = pygeoj.load(data=dict(...))

Basic information about the geojson file can then be extracted, such as:

::

    len(testfile) # the number of features
    testfile.bbox # the bounding box region of the entire file
    testfile.crs # the coordinate reference system
    testfile.all_attributes # retrieves the combined set of all feature attributes
    testfile.common_attributes # retrieves only those field attributes that are common to all features

Individual features can be accessed by their index in the features list:

::

    testfile[3]
    # or
    testfile.get_feature(3)

Or by iterating through all of them:

::

    for feature in testfile: 
        # do something

A feature can be inspected in various ways:

::

    feature.properties
    feature.geometry.type
    feature.geometry.coordinates
    feature.geometry.bbox

Editing
~~~~~~~

The standard Python list operations can be used to edit and swap around
the features in a geojson instance, and then saving to a new geojson
file:

::

    testfile[3] = testfile[8]
    # or testfile.replace_feature(3, testfile[8])
    del testfile[8]
    # or testfile.remove_feature(8)
    testfile.save("test_edit.geojson")

An existing feature can also be tweaked by using simple
attribute-setting:

::

    # set your own properties
    feature.properties = {"newfield1":"newvalue1", "newfield2":"newvalue2"}

    # borrow the geometry of the 16th feature
    feature.geometry = testfile[16].geometry

Note that when changing geometries or coordinates, you must remember to
update its bbox to clear away any older stored bbox information.

::

    feature.geometry.update_bbox()

Constructing
~~~~~~~~~~~~

Creating a new geojson file from scratch is also easy:

::

    newfile = pygeoj.new()

    # The data coordinate system defaults to long/lat WGS84 or can be manually defined:
    newfile.define_crs(type="link", link="http://spatialreference.org/ref/epsg/26912/esriwkt/", link_type="esriwkt")

The new file can then be populated with new features:

::

    newfile.add_feature(properties={"country":"Norway"},
                        geometry={"type":"Polygon", "coordinates":[[(21,3),(33,11),(44,22)]]} )
    newfile.add_feature(properties={"country":"USA"},
                        geometry={"type":"Polygon", "coordinates":[[(11,23),(14,5),(66,31)]]} )

Finally, some useful additional information can be added to top off the
geojson file before saving it to file:

::

    newfile.add_all_bboxes()
    newfile.update_bbox()
    newfile.add_unique_id()
    newfile.save("test_construct.geojson")

More Information:
-----------------

-  `Home Page <http://github.com/karimbahgat/PyGeoj>`__
-  `API Documentation <https://karimbahgat.github.io/PyGeoj/>`__

License:
--------

This code is free to share, use, reuse, and modify according to the MIT
license, see license.txt

Credits:
--------

-  Karim Bahgat
-  Mec-iS

Changes
-------

1.0.0 (2018-09-14)
~~~~~~~~~~~~~~~~~~

-  Bump to stable version
-  Officially support Python 3

0.2.5 (2017-02-19)
~~~~~~~~~~~~~~~~~~

-  Fixed more robust validation to avoid unexpected errors
-  Added skiperror option
-  Fixed feat type missing when add\_feature()
-  Fixed crs not saving
-  Added fixerror option when loading and validating
-  Fix bug to allow null geometries and empty properties, and correctly
   represent them in json as null

0.2.4 (2015-07-11)
~~~~~~~~~~~~~~~~~~

-  Fixed bug with add\_all\_bboxes() not updating existing bboxes
-  Fixed bug with GeojsonFile bbox sometimes being calculated wrong.
-  Added update\_bbox() on individual Geometry objects.
