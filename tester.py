import pygeoj as gj

testfile = gj.new()
testfile.add_feature(geometry=gj.Geometry(type="Point", coordinates=[(11,11)]),
                     properties=dict(hello=1, world=2))
testfile.add_feature(geometry=gj.Geometry(type="Point", coordinates=[(12,12)]),
                     properties=dict(hello=1, world=2))

for feat in testfile:
    feat.properties["new"] = "shit"
    feat.geometry.coordinates = (99,99)
    #feat.properties = dict(new="shit")
    #feat.geometry = gj.Geometry(type="Point", coordinates=(7777,7777))
    print "hmm", feat.geometry, feat.properties

for feat in testfile:
    print feat, feat.geometry, feat.properties, feat.validate()
