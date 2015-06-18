"""
# PyGeoj

PyGeoj is a simple Python GeoJSON file reader and writer intended for end-users.
It exposees dictionary structures as high level objects with convenience methods,
so the user does not have to get caught up in the details of the format specification. 


## Platforms

So far only tested on Python version 2.x. 


## Dependencies

Pure Python, no dependencies. 


## Installing it

PyGeoj is installed with pip from the commandline:

    pip install pygeoj

It also works to just place the "pygeoj" package folder in an importable location like 
"C:/PythonXX/Lib/site-packages". 


## Example Usage

Begin by importing the pygeoj module:

    import pygeoj

### Reading

Reading geojson formatted GIS files is a simple one-liner (requires the geojson file to be a
"FeatureCollection"):

    testfile = pygeoj.load(filepath="testfile.geojson")

Basic information about the geojson file can then be extracted, such as:

    len(testfile) # the number of features
    testfile.bbox # the bounding box region of the entire file
    testfile.crs # the coordinate reference system
    testfile.common_attributes # retrieves which field attributes are common to all features

Individual features can be accessed by their index in the features list:

    testfile[3]
    # or
    testfile.get_feature(3)

Or by iterating through all of them:

    for feature in testfile: 
        # do something

A feature can be inspected in various ways:

    feature.properties
    feature.geometry.type
    feature.geometry.coordinates
    feature.geometry.bbox

### Editing

The standard Python list operations can be used to edit and swap around the features in a geojson
instance, and then saving to a new geojson file:

    testfile[3] = testfile[8]
    # or testfile.replace_feature(3, testfile[8])
    del testfile[8]
    # or testfile.remove_feature(8)
    testfile.save("test_edit.geojson")

An existing feature can also be tweaked by using simple attribute-setting:

    # set your own properties
    feature.properties = {"newfield1":"newvalue1", "newfield2":"newvalue2"}

    # borrow the geometry of the 16th feature
    feature.geometry = testfile[16].geometry

### Constructing

Creating a new geojson file from scratch is also easy:

    newfile = pygeoj.new()

    # The data coordinate system defaults to long/lat WGS84 or can be manually defined:
    newfile.define_crs(type="link", link="http://spatialreference.org/ref/epsg/26912/esriwkt/", link_type="esriwkt")

The new file can then be populated with new features:

    newfile.add_feature(properties={"country":"Norway"},
                        geometry={type="Polygon", coordinates=[[(21,3),(33,11),(44,22)]]} )
    newfile.add_feature(properties={"country":"USA"},
                        geometry={type="Polygon", coordinates=[[(11,23),(14,5),(66,31)]]} )

Finally, some useful additional information can be added to top off the geojson file before saving it to
file:
 
    newfile.add_all_bboxes()
    newfile.add_unique_id()
    newfile.save("test_construct.geojson")


## More Information:

- [Home Page](http://github.com/karimbahgat/PyGeoj)
- [API Documentation](http://pythonhosted.org/PyGeoj)


## License:

This code is free to share, use, reuse,
and modify according to the MIT license, see license.txt


## Credits:

Karim Bahgat (2015)

"""

__version__ = "0.22"

try:
    import simplejson as json
except:
    import json

class Geometry:
    """
    A geometry instance, as an object representation of GeoJSON's geometry dictinoary item,
    with some convenience methods. 

    Attributes:
 
    - **type**: As specified when constructed
    - **coordinates**: As specified when constructed
    - **bbox**: If the bounding box wasn't specified when constructed then it is calculated on-the-fly.
    """
    def __init__(self, obj=None, type=None, coordinates=None, bbox=None):
        """
        Can be created from args, or without any to create an empty one from scratch.
        If obj isn't specified, type, coordinates, and optionally bbox can be set as arguments

        Parameters:
        
        - **obj**:
            Another geometry instance, an object with the \_\_geo_interface__ or a geojson dictionary of the Geometry type
        - **type** (optional):
            The type of geometry. Point, MultiPoint, LineString, MultiLineString,
            Polygon, or MultiPolygon. 
        - **coordinates** (optional):
            A sequence of coordinates formatted according to the geometry type. 
        - **bbox** (optional):
            The bounding box of the geometry as [xmin, ymin, xmax, ymax].
        """
        if isinstance(obj, Geometry):
            self._data = obj._data.copy()
        elif hasattr(obj, "__geo_interface__"):
            self._data = obj.__geo_interface__
        elif isinstance(obj, dict):
            self._data = obj
        elif type and coordinates:
            _data = {"type":type,"coordinates":coordinates}
            if bbox: _data.update({"bbox":bbox})
            self._data = _data
        else:
            # empty geometry dictionary
            self._data = {}

    def __setattr__(self, name, value):
        """Set a class attribute like obj.attr = value"""
        try: self._data[name] = value # all attribute setting will directly be redirected to adding or changing the geojson dictionary entries
        except AttributeError: self.__dict__[name] = value # except for first time when the _data attribute has to be set

    def __str__(self):
        return "Geometry(type=%s, coordinates=%s, bbox=%s)" % (self.type, self.coordinates, self.bbox)

    @property
    def __geo_interface__(self):
        return self._data.copy()

    # Attributes

    @property
    def type(self):
        return self._data["type"]

    @property
    def bbox(self):
        if self._data.get("bbox"): return self._data["bbox"]
        else:
            if self.type == "Point":
                x,y = self._data["coordinates"]
                return [x,y,x,y]
            elif self.type in ("MultiPoint","LineString"):
                coordsgen = (point for point in self._data["coordinates"])
            elif self.type == "MultiLineString":
                coordsgen = (point for line in self._data["coordinates"] for point in line)
            elif self.type == "Polygon":
                coordsgen = (point for point in self._data["coordinates"][0]) # only the first exterior polygon should matter for bbox, not any of the holes
            elif self.type == "MultiPolygon":
                coordsgen = (point for polygon in self._data["coordinates"] for point in polygon[0]) # only the first exterior polygon should matter for bbox, not any of the holes
            firstpoint = next(coordsgen)
            _xmin = _xmax = firstpoint[0]
            _ymin = _ymax = firstpoint[1]
            for _x,_y in coordsgen:
                if _x < _xmin: _xmin = _x
                elif _x > _xmax: _xmax = _x
                if _y < _ymin: _ymin = _y
                elif _y > _ymax: _ymax = _y
            return _xmin,_ymin,_xmax,_ymax
    
    @property
    def coordinates(self):
        return self._data["coordinates"]

    # Methods

    def validate(self):
        """
        Validates that the geometry is correctly formatted according to the geometry type. 

        Returns:
        
        - True if the geometry is valid.

        Raises:

        - An Exception if not valid. 
        """
        
        # first validate geometry type
        if not self.type in ("Point","MultiPoint","LineString","MultiLineString","Polygon","MultiPolygon"):
            raise Exception('Invalid geometry type. Must be one of: "Point","MultiPoint","LineString","MultiLineString","Polygon","MultiPolygon"')

        # then validate coordinate data type
        coords = self._data["coordinates"]
        if not isinstance(coords, (list,tuple)): raise Exception("Coordinates must be a list or tuple type")

        # then validate coordinate structures
        if self.type == "Point":
            if not len(coords) == 2: raise Exception("Point must be one coordinate pair")
        elif self.type in ("MultiPoint","LineString"):
            if not len(coords) > 1: raise Exception("MultiPoint and LineString must have more than one coordinates")
        elif self.type == "MultiLineString":
            if not len(coords) > 1: raise Exception("MultiLineString must have more than one LineString member")
            for line in coords:
                if not len(line) > 1: raise Exception("All LineStrings in a MultiLineString must have more than one coordinate")
        elif self.type == "Polygon":
            for exterior_or_holes in coords:
                if not len(exterior_or_holes) >= 3: raise Exception("The exterior and all holes in a Polygon must have at least 3 coordinates")
        elif self.type == "MultiPolygon":
            if not len(coords) > 1: raise Exception("MultiPolygon must have more than one Polygon member")
            for eachmulti in coords:
                for exterior_or_holes in eachmulti:
                    if not len(exterior_or_holes) >= 3: raise Exception("The exterior and all holes in all Polygons of a MultiPolygon must have at least 3 coordinates")

        # validation successful
        return True



class Feature(object):
    """
    A feature instance, as an object representation of GeoJSON's feature dictinoary item,
    with some convenience methods. 

    Attributes:

    - **geometry**: A Geometry instance.
    - **properties**: A properties dictionary
    """
    def __init__(self, obj=None, geometry=None, properties={}):
        """
        If obj isn't specified, geometry and properties can be set as arguments directly.

        Parameters:

        - **obj**: Another feature instance, an object with the \_\_geo_interface__ or a geojson dictionary of the Feature type.
        - **geometry** (optional): Anything that the Geometry instance can accept.
        - **properties** (optional): A dictionary of key-value property pairs.
        """
        if isinstance(obj, Feature):
            # from scrath as copy of another feat instance
            self._data = {"type":"Feature",
                          "geometry":Geometry(obj.geometry).__geo_interface__,
                          "properties":obj.properties.copy() }
        elif isinstance(obj, dict):
            # comes straight from geojfile _iter_, so must use original dict
            self._data = obj
        elif geometry:
            # from scratch from geometry/properties
            self._data = {"type":"Feature",
                          "geometry":Geometry(geometry).__geo_interface__,
                          "properties":properties }

    def __str__(self):
        return "Feature(geometry=%s, properties=%s)" % (self.geometry, self.properties)

    @property
    def __geo_interface__(self):
        geojdict = {"type":"Feature",
                    "geometry":self.geometry.__geo_interface__,
                    "properties":self.properties }
        return geojdict

    @property
    def properties(self):
        return self._data["properties"]

    @properties.setter
    def properties(self, value):
        self._data["properties"].clear()
        self._data["properties"].update(**value)

    @property
    def geometry(self):
        return Geometry(self._data["geometry"])

    @geometry.setter
    def geometry(self, value):
        if isinstance(value, Geometry):
            value = value.__geo_interface__
        self._data["geometry"].update(**value)

    def validate(self):
        """
        Validates that the feature is correctly formatted. 

        Returns:
        
        - True if the feature is valid.

        Raises:

        - An Exception if not valid. 
        """
        if not isinstance(self.properties, dict): raise Exception("The 'properties' value of a geojson feature must be a dictionary type")
        self.geometry.validate()
        return True
    

class GeojsonFile:
    """
    An instance of a geojson file. 

    Attributes:

    - **crs**: The geojson formatted dictionary of the file's coordinate reference system. Read only. Call .define_crs() to change it. 
    - **bbox**: The bounding box surrounding all geometries in the file. Read only. You may need to call .update_bbox() to make sure this one is up-to-date.
    - **all_attributes**: Collect and return a list of all attributes/properties/fields used in any of the features. Read only. 
    - **common_attributes**: Collects and returns a list of attributes/properties/fields common to all features. Read only. 
    """
    
    def __init__(self, filepath=None, data=None, **kwargs):
        """
        Can load from data or from a file,
        which can then be read or edited.
        Call without any arguments to create an empty geojson file
        so you can construct it from scratch.

        In order for a geojson dict to be considered a file,
        it cannot just be single geometries, so this class always
        saves them as the toplevel FeatureCollection type,
        and requires the files it loads to be the same.

        Parameters:
        
        - **filepath** (optional): The path of a geojson file to load.
        - **data** (optional): A complete geojson dictionary to load.
        """
        if filepath:
            data = self._loadfilepath(filepath, **kwargs)
            if self._validate(data):
                self._data = self._prepdata(data)
        elif data:
            if self._validate(data):
                self._data = self._prepdata(data)
        else:
            self._data = dict([("type","FeatureCollection"),
                               ("features",[]),
                               ("crs",{"type":"name",
                                       "properties":{"name":"urn:ogc:def:crs:OGC:2:84"}}) ])

    def __len__(self):
        return len(self._data["features"])

##    def __setattr__(self, name, value):
##        """Set a class attribute like obj.attr = value"""
##        try: self._data[name] = value # all attribute setting will directly be redirected to adding or changing the geojson dictionary entries
##        except AttributeError: self.__dict__[name] = value # except for first time when the _data attribute has to be set

    def __getitem__(self, index):
        """Get a feature based on its index, like geojfile[7]"""
        return Feature(self._data["features"][index])

    def __setitem__(self, index, feature):
        """Replace a feature based on its index with a new one (same requirements as Feature's obj arg),
        like geojfile[7] = newfeature
        """
        self._data["features"][index] = feature

    def __delitem__(self, index):
        """Delete a feature based on its index, like del geojfile[7]"""
        del self._data["features"][index]
        
    def __iter__(self):
        """Iterates through and yields each feature in the file."""
        for featuredict in self._data["features"]:
            yield Feature(featuredict)

    @property
    def __geo_interface__(self):
        return self._data

    # Attributes
                         
    @property
    def crs(self):
        type = self._data["crs"]["type"]
        if type not in ("name","link"): raise Exception("invalid crs type: must be either name or link")
        return self._data["crs"]

    @property
    def bbox(self):
        if self._data.get("bbox"):
            return self._data["bbox"]
        else: return None # file must be new and therefore has no feature geometries that can be used to calculate bbox

    @property
    def all_attributes(self):
        """
        Collect and return a list of all attributes/properties/fields used in any of the features.
        """
        features = self._data["features"]
        if not features: return []
        elif len(features) == 1: return features[0]["properties"].keys()
        else:
            fields = set(features[0]["properties"].keys())
            for feature in features[1:]:
                fields.update(feature["properties"].keys())
            return list(fields)

    @property
    def common_attributes(self):
        """
        Collect and return a list of attributes/properties/fields common to all features.
        """
        features = self._data["features"]
        if not features: return []
        elif len(features) == 1: return features[0]["properties"].keys()
        else:
            fields = set(features[0]["properties"].keys())
            for feature in features[1:]:
                fields.intersection_update(feature["properties"].keys())
            return list(fields)

    # Methods

    def add_feature(self, obj=None, geometry=None, properties={}):
        """
        Adds a given feature. If obj isn't specified, geometry and properties can be set as arguments directly.

        Parameters:

        - **obj**: Another feature instance, an object with the \_\_geo_interface__ or a geojson dictionary of the Feature type.
        - **geometry** (optional): Anything that the Geometry instance can accept.
        - **properties** (optional): A dictionary of key-value property pairs.
        """
        if isinstance(obj, Feature):
            feat = obj.__geo_interface__
        elif isinstance(obj, dict):
            feat = obj.copy()
        elif geometry:
            feat = dict(geometry=Geometry(geometry).__geo_interface__, properties=properties)
        self._data["features"].append(feat)

    def get_feature(self, index):
        """
        Gets a feature based on its index. Same as feat[index]. 

        Parameters:

        - **index**: The index position of the feature to get.

        Returns:

        - A Feature instance. 
        """
        return self[oldindex]

    def replace_feature(self, oldindex, newfeature):
        """
        Replaces the feature at an index position with another. 

        Parameters:

        - **oldindex**: The index position of the feature to be replaced. 
        - **newfeature**: Anything that the Feature instance can accept.
        """
        self[oldindex] = newfeature

    def remove_feature(oldindex):
        """
        Removes a feature at a specified index position. 

        Parameters:

        - **oldindex**: The index position of the feature to be removed. 
        """
        del self[oldindex]

    def addfeature(self, feature):
        """
        Backwards compatible legacy method. WARNING: Will be depreceated. 
        """
        self.add_feature(obj=feature)

    def getfeature(self, index):
        """
        Backwards compatible legacy method. WARNING: Will be depreceated. 
        """
        self.get_feature(index)

    def replacefeature(self, oldindex, newfeature):
        """
        Backwards compatible legacy method. WARNING: Will be depreceated. 
        """
        self.replace_feature(oldindex, newfeature)

    def removefeature(oldindex):
        """
        Backwards compatible legacy method. WARNING: Will be depreceated. 
        """
        self.remove_feature(oldindex)
        
    def define_crs(self, type, name=None, link=None, link_type=None):
        """
        Defines the coordinate reference system for the geojson file.
        For link crs, only online urls are currenlty supported
        (no auxilliary crs files).

        Parameters:

        - **type**: The type of crs, either "name" or "link".
        - **name** (optional): The crs name as an OGC formatted crs string (eg "urn:ogc:def:crs:..."), required if type is "name"
        - **link**: The crs online url link address, required if type is "link".
        - **link_type**: The type of crs link, optional if type is "link". 
        """
        if not type in ("name","link"): raise Exception("type must be either 'name' or 'link'")
        self.crs = {"type":type, "properties":{} }
        if type == "name":
            if not name: raise Exception("name argument must be given")
            self.crs["properties"]["name"] = name
        elif type == "link":
            if not link: raise Exception("link argument must be given")
            self.crs["properties"]["href"] = link
            if link_type:
                self.crs["properties"]["type"] = link_type

    def update_bbox(self):
        """
        Recalculates the bbox region attribute for the entire file.
        Useful after adding and/or removing features.

        No need to use this method just for saving, because saving
        automatically updates the bbox.
        """

        firstfeature = Feature(self._data["features"][0])
        xmin,xmax,ymin,ymax = firstfeature.geometry.bbox
        for _featuredict in self._data["features"][1:]:
            _xmin,_xmax,_ymin,_ymax = Feature(_featuredict).geometry.bbox
            if _xmin < xmin: xmin = _xmin
            elif _xmax > xmax: xmax = _xmax
            if _ymin < ymin: ymin = _ymin
            elif _ymax > ymax: ymax = _ymax
            
        self._data["bbox"] = [xmin,ymin,xmax,ymax]

    def add_unique_id(self):
        """
        Adds a unique id property to each feature.

        Raises:
        
        - An Exception if any of the features already
            have an "id" field. 
        """
        
        uid = 0
        for feature in self._data["features"]:
            if feature["properties"].get("id"):
                raise Exception("one of the features already had an id field")
            feature["properties"]["id"] = uid
            uid += 1

    def add_all_bboxes(self):
        """
        Calculates and adds a bbox attribute to all feature geometries.
        """
        for feature in self._data["features"]:
            if not feature["geometry"].get("bbox"):
                feature["geometry"]["bbox"] = Feature(feature).geometry.bbox

    def save(self, savepath, **kwargs):
        """
        Saves the geojson instance to file. To save with a different text encoding use the 'encoding' argument.

        Parameters:

        - **savepath**: Filepath to save the file. 
        """
        
        self.update_bbox()
        tempfile = open(savepath,"w")
        json.dump(self._data, tempfile, **kwargs)
        tempfile.close()

    # Internal Methods
                         
    def _validate(self, data):
        """Checks that the geojson data is a feature collection, and that it
        contains a proper "features" attribute, and returns True if so."""
        if not data["type"] == "FeatureCollection":
            raise ValueError("The geojson data needs to be a feature collection")
        if data.get("features"):
            if not isinstance(data["features"], list):
                raise ValueError("The features property needs to be a list")
            return True
        else: raise ValueError("The FeatureCollection needs to contain a 'features' property")

    def _loadfilepath(self, filepath, **kwargs):
        """This loads a geojson file into a geojson python
        dictionary using the json module.
        
        Note: to load with a different text encoding use the encoding argument.
        """
        data = json.load(open(filepath,"rU"), **kwargs)
        return data

    def _prepdata(self, data):
        """Adds potentially missing items to the geojson dictionary"""
        
        # if missing, compute and add bbox
        if not data.get("bbox"):
            
            firstfeature = Feature(data["features"][0])
            xmin,xmax,ymin,ymax = firstfeature.geometry.bbox
            for _featuredict in data["features"][1:]:
                _xmin,_xmax,_ymin,_ymax = Feature(_featuredict).geometry.bbox
                if _xmin < xmin: xmin = _xmin
                elif _xmax > xmax: xmax = _xmax
                if _ymin < ymin: ymin = _ymin
                elif _ymax > ymax: ymax = _ymax
                
            data["bbox"] = [xmin,ymin,xmax,ymax]
                
        # if missing, set crs to default crs (WGS84), see http://geojson.org/geojson-spec.html
        if not data.get("crs"):
            data["crs"] = {"type":"name",
                           "properties":{"name":"urn:ogc:def:crs:OGC:2:84"}}
            
        return data



# User functions

def load(filepath=None, data=None, **kwargs):
    """
    Loads a geojson file or dictionary, validates it, and returns a
    GeojsonFile instance.

    In order for a geojson dict to be considered a file,
    it cannot just be single geometries, so this class always
    saves them as the toplevel FeatureCollection type,
    and requires the files it loads to be the same.

    To load with a different text encoding use the 'encoding' argument.

    Parameters:

    - **filepath** (optional): The path of a geojson file to load.
    - **data** (optional): A complete geojson dictionary to load.

    Returns:

    - A GeojsonFile instance.
    """
    return GeojsonFile(filepath, data, **kwargs)

def new():
    """
    Creates a new empty geojson file instance.

    Returns:

    - An empty GeojsonFile instance. 
    """
    return GeojsonFile()






    
    
            
