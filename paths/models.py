from neomodel import (StructuredNode, StructuredRel, StringProperty, IntegerProperty,RelationshipTo,FloatProperty, Relationship)


class WayRel(StructuredRel):
    osmID = IntegerProperty(required=True)
    name = StringProperty()
    vnormal = FloatProperty(default=1.0)
    vrush =  FloatProperty(default=1.0)
    risk = FloatProperty(default=50.0)
    distance = FloatProperty(default=100)

class Point(StructuredNode):
    osmID = IntegerProperty(unique_index=True, required=True)
    lat = FloatProperty(required=True)
    lon = FloatProperty(required=True)

    way = RelationshipTo('Point', 'Way', model=WayRel)


