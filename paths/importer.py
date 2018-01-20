from paths.models import Point
from osmread import parse_file, Way, Node
from vincenty import vincenty
from time import gmtime, strftime
from datetime import datetime
from py2neo import authenticate, Graph
from neomodel import db

file = "C:/Users/Avell/Desktop/MONO/slz2.osm"

def checkNode(osmIdTemp, fullNodes):
    try:
        point = Point.nodes.get(osmID=osmIdTemp)
    except Point.DoesNotExist:
         point = Point(osmID=fullNodes[osmIdTemp].id, lat= fullNodes[osmIdTemp].lat, lon=fullNodes[osmIdTemp].lon)
         point.save()          
    return point

def importer():
        
    fullnodes = {}
    
    highway_count = 0
    rua = []
    tipo = ['pedestrian', 'raceway', 'footway', 'steps', 'paths']
    for entity in parse_file(file):
        if isinstance(entity, Way) and 'highway' in entity.tags and entity.tags['highway'] not in tipo:
            highway_count += 1
            rua.append(entity)
        if isinstance(entity, Node):
            fullnodes[entity.id] = entity
    k=0
    for way in rua:
        nodes = way.nodes
        print(datetime.now().strftime("[%H:%M:%S]") + ": PROCESSANDO WAY: " + str(way.id))
        startNode = Point.get_or_create({'osmID': nodes[0], 'lat':fullnodes[nodes[0]].lat, 'lon': fullnodes[nodes[0]].lon})[0] 
        for i in range(0, len(nodes) - 1):
            #startNode = checkNode(nodes[i], fullnodes)            
            endNode = Point.get_or_create({'osmID': nodes[i+1], 'lat':fullnodes[nodes[i+1]].lat, 'lon': fullnodes[nodes[i+1]].lon})[0] 

            start = (startNode.lat,startNode.lon)
            end = (endNode.lat, endNode.lon)
            distance = vincenty(start, end)
            
            name = " "
            if 'name' in way.tags:
                name = way.tags['name']
    
            wayRel = startNode.way.connect(endNode, {'osmID': way.id, 'name': name, 'distance': distance})
            wayRel.save()
            if (('oneway' not in way.tags) or ('oneway' in way.tags and way.tags['oneway'] != 'yes')) and ('junction' not in way.tags):
               returnRel = endNode.way.connect(startNode, {'osmID': way.id, 'name': name, 'distance': distance})
               returnRel.save()
            startNode = endNode
        k+= 1
        print(datetime.now().strftime("[%H:%M:%S]") + ": CRIADO WAY: " + str(way.id) + " - " + str(k))
    print("%d highways found" % highway_count)
    
def importer2():
        
    fullnodes = {}
    
    highway_count = 0
    rua = []
    tipo = ['pedestrian', 'raceway', 'footway', 'steps', 'paths']
    for entity in parse_file(file):
        if isinstance(entity, Way) and 'highway' in entity.tags and entity.tags['highway'] not in tipo:
            highway_count += 1
            rua.append(entity)
        if isinstance(entity, Node):
            fullnodes[entity.id] = entity
    k=0
    for way in rua:
        nodes = way.nodes
        print(datetime.now().strftime("[%H:%M:%S]") + ": PROCESSANDO WAY: " + str(way.id) + " -> " + str(len(nodes)))


        if k < 957:
            print('OK')
        else: 
            query = '''MERGE (:Point {{osmID: {0}, lat: {1}, lon:{2} }}) '''.format(nodes[0],fullnodes[nodes[0]].lat,fullnodes[nodes[0]].lon)
    
            startOSM, meta = db.cypher_query(query)

        startID = nodes[0]
        
        for i in range(0, len(nodes) - 1):
            if k < 957:
                print('OK')
            else: 
                #startNode = checkNode(nodes[i], fullnodes)            
                query = '''MERGE (:Point {{osmID: {0}, lat: {1}, lon:{2} }}) '''.format(nodes[i+1],fullnodes[nodes[i+1]].lat,fullnodes[nodes[i+1]].lon)
                endOSM, meta = db.cypher_query(query)

                endID = nodes[i+1]
                start = (fullnodes[nodes[i]].lat,fullnodes[nodes[i]].lon)
                end = (fullnodes[nodes[i+1]].lat, fullnodes[nodes[i+1]].lon)
                distance = vincenty(start, end)
          
                name = " "
                if 'name' in way.tags:
                    name = way.tags['name']

                query = '''MATCH (startpoint:Point {{ osmID: {0} }}),(endpoint:Point {{ osmID: {1} }})
                           CREATE  (startpoint)-[r:Way {{osmID: {2}, name: "{3}", distance: {4} }}]->(endpoint)'''.format(startID,endID,way.id,name,distance)

                wayRelFoward, meta = db.cypher_query(query)

                if (('oneway' not in way.tags) or ('oneway' in way.tags and way.tags['oneway'] != 'yes')) and ('junction' not in way.tags):
                     query = '''MATCH (startpoint:Point {{ osmID: {0} }}),(endpoint:Point {{ osmID: {1} }})
                           CREATE (endpoint)-[r:Way {{osmID: {2}, name: "{3}", distance: {4} }}]->(startpoint)'''.format(startID,endID,way.id,name,distance)
                     wayRelReverse, meta = db.cypher_query(query)
                startID = endID
        k+= 1
        print(datetime.now().strftime("[%H:%M:%S]") + ": CRIADO WAY: " + str(way.id) + " - " + str(k))
    print("%d highways found" % highway_count)
