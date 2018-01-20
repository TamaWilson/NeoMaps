from django.shortcuts import render
from paths.utilpaths import getRelWay

from neomodel import db
# Create your views here.
from paths.models import Point, WayRel

def index(request):
    context = {}
    return render(request, 'paths/index.html', context)


def results(request):
    start = [float(x) for x in request.POST['startpoint'].replace("LatLng(", "").replace(")", "").split(',')]
    end = [float(x) for x in request.POST['endpoint'].replace("LatLng(", "").replace(")", "").split(',')]

    startOSM = getRelWay(start)
    endOSM = getRelWay(end)

    query = '''MATCH (start:Point {{osmID: {0} }}), (end:Point {{osmID: {1} }})
                       CALL apoc.algo.dijkstra(start, end, 'Way>', 'distance') YIELD path, weight
                       RETURN path, weight'''.format(startOSM[0][0], endOSM[0][0])

    path, meta = db.cypher_query(query)
    rawPath = path[0][0]
    nodes = [[Point.inflate(row).lat, Point.inflate(row).lon] for row in rawPath.nodes]

    polyline = 'new L.LatLng({0}, {1}),\n'.format(start[0],start[1])

    for node in nodes:
        polyline +=  'new L.LatLng({0}, {1}),\n'.format(node[0],node[1])

    polyline += 'new L.LatLng({0}, {1}),\n'.format(end[0],end[1])

    context = { 'start': startOSM[0], 'end': endOSM[0], 'polyline' : polyline, 'meta' : path[0][1]}

    return render(request, 'paths/results.html', context)