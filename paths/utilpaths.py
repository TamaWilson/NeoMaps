from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import re
from neomodel import db


def getRelWay(tempPoint):


    url = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={0}&lon={1}".format(tempPoint[0], tempPoint[1])
    rawResponse = urlopen(url)
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

    pointOSM, meta = db.cypher_query(query)

    return pointOSM