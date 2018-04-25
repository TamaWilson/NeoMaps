from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import json
import re
from neomodel import db
import time
import logging

# Get an instance of a logger
logger = logging.getLogger('testes')
def getRelWay(tempPoint):
    logger.debug("{0}:{1}".format(time.strftime("%H:%M:%S"), tempPoint))
    try:
        url = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={0}&lon={1}&zoom=16".format(tempPoint[0], tempPoint[1])
        req =  Request(url)
        logger.debug("{0}:{1}".format(time.strftime("%H:%M:%S"), url))
        req.headers['User-Agent'] = 'OSMPythonTools/0.1.8 (https://github.com/mocnik-science/osm-python-tools)'

        rawResponse = urlopen(req)

        tempWay = json.loads(rawResponse.read().decode("utf-8"))

        if tempWay['osm_type'] != 'way':
            details_url = "https://nominatim.openstreetmap.org/details.php?place_id=" + tempWay['place_id']
            html = urlopen(details_url)
            bsObj = BeautifulSoup(html.read(), 'html.parser')

            rawDetails = bsObj.find('td', text=re.compile('highway*')).parent
            wayRaw = rawDetails.findAll("a", text=re.compile('way*'))[0].text
            osmID = re.sub("[^0-9]", "", wayRaw)
        else:
            osmID = tempWay["osm_id"]

        query = '''WITH {0} AS lat, {1} AS lon, 
                   point({{ longitude: {1}, latitude: {0} }}) AS tempPoint 
                   MATCH (l:Point)-[r:Way]->()
                   WHERE 2 * 6371 * asin(sqrt(haversin(radians(lat - l.lat))+ cos(radians(lat))* cos(radians(l.lat))* haversin(radians(lon - l.lon)))) < 999999999
                   AND r.osmID = {2}
                   RETURN l.osmID, MIN(DISTANCE(tempPoint,point({{longitude: l.lon, latitude: l.lat}}))) as dis
                   order by dis asc limit 1'''.format(tempPoint[0],tempPoint[1],osmID)
        otimized = True
        pointOSM, meta = db.cypher_query(query)

        if len(pointOSM) == 0:
            raise Exception("PointOSM: {0}".format(pointOSM))
    except Exception as e:
        logger.debug("{0}:{1}".format(time.strftime("%H:%M:%S"), e))
        query = '''WITH {0} AS lat, {1} AS lon, 
                           point({{ longitude: {1}, latitude: {0} }}) AS tempPoint 
                           MATCH (l:Point)-[r:Way]->()
                           WHERE 2 * 6371 * asin(sqrt(haversin(radians(lat - l.lat))+ cos(radians(lat))* cos(radians(l.lat))* haversin(radians(lon - l.lon)))) < 999999999
                           
                           RETURN l.osmID, MIN(DISTANCE(tempPoint,point({{longitude: l.lon, latitude: l.lat}}))) as dis
                           order by dis asc limit 1'''.format(tempPoint[0], tempPoint[1])
        otimized = False
        pointOSM, meta = db.cypher_query(query)
    pointOSM[0].append(otimized)
    return pointOSM
