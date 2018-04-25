from neomodel import (StructuredNode, StructuredRel, StringProperty, IntegerProperty,RelationshipTo,FloatProperty, BooleanProperty)

class DateNode(StructuredNode):
    date = IntegerProperty(required=True)


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
    feq = IntegerProperty(default=0)
    way = RelationshipTo('Point', 'Way', model=WayRel)

class Metric(StructuredNode):
    startPoint = StringProperty()
    endPoint = StringProperty()
    startId = IntegerProperty()
    endId = IntegerProperty()
    otimizedStart = BooleanProperty()
    otimizedEnd =  BooleanProperty()
    metric = FloatProperty()
    hour = StringProperty()
    status = StringProperty()	
    mensured = RelationshipTo(DateNode, "MENSURED_ON")