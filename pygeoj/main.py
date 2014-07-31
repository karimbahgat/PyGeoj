"""
A simple Python Geojson file reader and writer.
Author: Karim Bahgat, 2014
Contact: karim.bahgat.norway@gmail.com
License: MIT License
"""

try:
    import simplejson as json
except:
    import json

class Geometry:
    """
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
    """
    
    def __init__(self, obj=None, type=None, coordinates=None, bbox=None):
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

    @property
    def __geo_interface__(self):
        return self._data

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
        Validates that the geometry is correctly formatted, and raises an error if not
        """
        
        # first validate geometry type
        if not self.type in ("Point","MultiPoint","LineString","MultiLineString","Polygon","MultiPolygon"):
            raise Exception('Invalid geometry type. Must be one of: "Point","MultiPoint","LineString","MultiLineString","Polygon","MultiPolygon"')

        # then validate coordinate data type
        coords = self._data["coordinates"]
        if not isinstance(coords, (list,tuple)): raise Exception("Coordinates must be a list or tuple type")

        # then validate coordinate structures
        if self.type == "Point":
            if not len(coords) == 1: raise Exception("Point must be one coordinate")
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



class Feature:
    """
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
    """
    
    def __init__(self, obj=None, geometry=None, properties={}):
        if isinstance(obj, Feature):
            self.geometry = Geometry(obj.geometry)
            self.properties = obj.properties.copy()
        elif isinstance(obj, dict):
            self.geometry = Geometry(obj["geometry"])
            self.properties = obj["properties"]
        elif geometry:
            self.geometry = Geometry(geometry)
            self.properties = properties

    @property
    def __geo_interface__(self):
        geojdict = {"type":"Feature",
                    "geometry":self.geometry.__geo_interface__,
                    "properties":self.properties }
        return geojdict

    def validate(self):
        """
        Validates that the feature is correctly formatted, and raises an error if not
        """
        if not isinstance(self.properties, dict): raise Exception("The 'properties' value of a geojson feature must be a dictionary type")
        self.geometry.validate()
    

class GeojsonFile:
    """
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
    """
    
    def __init__(self, filepath=None, data=None, **kwargs):
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

    def __setattr__(self, name, value):
        """Set a class attribute like obj.attr = value"""
        try: self._data[name] = value # all attribute setting will directly be redirected to adding or changing the geojson dictionary entries
        except AttributeError: self.__dict__[name] = value # except for first time when the _data attribute has to be set

    def __getitem__(self, index):
        """Get a feature based on its index, like geojfile[7]"""
        return Feature(self._data["features"][index])

    def __setitem__(self, index, feature):
        """Replace a feature based on its index with a new one (must have __geo_interface__ property),
        like geojfile[7] = newfeature
        """
        self._data["features"][index] = feature.__geo_interface__
        
    def __iter__(self):
        """Iterates through and returns a record list and a
        shape instance for each feature in the file.
        """
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
    def common_attributes(self):
        """
        Collect and return a list of attributes/properties/fields common to all features
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

    def getfeature(self, index):
        return Feature(self._data["features"][index])

    def addfeature(self, feature):
        feature = Feature(feature)
        self._data["features"].append(feature.__geo_interface__)

    def insertfeature(self, index, feature):
        feature = Feature(feature)
        self._data["features"].insert(index, feature.__geo_interface__)

    def replacefeature(self, replaceindex, newfeature):
        newfeature = Feature(newfeature)
        self._data["features"][replaceindex] = newfeature.__geo_interface__

    def removefeature(self, index):
        self._data["features"].pop(index)

    def define_crs(self, type, name=None, link=None, link_type=None):
        """
        Defines the coordinate reference system for the geojson file.
        Note: for link crs, only online urls are supported
        (no auxilliary crs files)

        | __option__    | __description__ 
        | --- | --- 
        | type | the type of crs, either "name" or "link"
        | name | the crs name as an OGC formatted crs string (eg "urn:ogc:def:crs:..."), required if type is "name"
        | link | the crs online url link address, required if type is "link"
        | link_type | the type of crs link, optional if type is "link"
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
        Recalculates the bbox region for the entire shapefile.
        Useful after adding and/or removing features.
        Note: No need to use this method just for saving, because saving
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
        Note: Results in error if any of the features already
        have an "id" field
        """
        
        uid = 0
        for feature in self._data["features"]:
            if feature["properties"].get("id"):
                raise Exception("one of the features already had an id field")
            feature["properties"]["id"] = uid
            uid += 1

    def add_all_bboxes(self):
        """
        Calculates and adds a bbox attribute to all feature geometries
        """
        for feature in self._data["features"]:
            if not feature["geometry"].get("bbox"):
                feature["geometry"]["bbox"] = Feature(feature).geometry.bbox

    def save(self, savepath, **kwargs):
        """
        Saves the geojson instance to file.
        Note: to save with a different text encoding use the 'encoding' argument.

        | __option__    | __description__ 
        | --- | ---
        | savepath | filepath to save the file
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

    Note: In order for a geojson dict to be considered a file,
    it cannot just be single geometries, so this class always
    saves them as the toplevel FeatureCollection type,
    and requires the files it loads to be the same.

    Note: to load with a different text encoding use the 'encoding' argument.

    | __option__    | __description__ 
    | --- | --- 
    | filepath | the path of a geojson file to load (optional).
    | data | a complete geojson dictionary to load (optional).
    """
    return GeojsonFile(filepath, data, **kwargs)

def new():
    """
    Creates and returns a new empty geojson file instance.
    """
    return GeojsonFile()






    
    
            
