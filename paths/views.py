from django.shortcuts import render, redirect
from django.contrib import messages
from paths.utilpaths import getRelWay
import time
from datetime import datetime
from neomodel import db
# Create your views here.
from paths.models import Point, WayRel, Metric, DateNode

def index(request):
    context = {}
    storage = messages.get_messages(request)
    for message in storage:
        context = {'ex': message}
    return render(request, 'paths/index.html', context)

def teste(request):
    context = {'start': [-2.53342,-44.28391,10], 'end': [-2.5335509,-44.28449,12]}
    return render(request, 'paths/teste.html', context)


def results(request):
    if not request.POST['startpoint'].strip() or not request.POST['endpoint'].strip():
        messages.add_message(request, messages.INFO, "Informe a origem e o destino da rota!")
        return redirect('/')
    db.begin()
    try:
        start_time = time.time()

        start = [float(x) for x in request.POST['startpoint'].replace("LatLng(", "").replace(")", "").split(',')]
        end = [float(x) for x in request.POST['endpoint'].replace("LatLng(", "").replace(")", "").split(',')]

        #time.sleep(1)
        startOSM = getRelWay(start)
        #time.sleep(1)
        endOSM = getRelWay(end)

        query = '''MATCH (start:Point {{osmID: {0} }}), (end:Point {{osmID: {1} }})
                           CALL apoc.algo.dijkstra(start, end, 'Way>', 'distance') YIELD path, weight
                           RETURN path, weight'''.format(startOSM[0][0], endOSM[0][0])

        path, meta = db.cypher_query(query)

        rawPath = path[0][0]

        nodes = []
        for row in rawPath.nodes:
            nodeTemp = Point.inflate(row)
            nodeTemp.feq += 1
            nodeTemp.save()
            nodes.append([nodeTemp.lat, nodeTemp.lon,nodeTemp.feq])

        query = 'MATCH(n) WHERE EXISTS(n.feq) RETURN max(n.feq)'

        max, meta = db.cypher_query(query)

        hotline = '[{0},{1},0],'.format(start[0],start[1])

        for node in nodes:

            hotline += '[{0},{1},{2}],'.format(node[0], node[1], node[2])
        hotline += '[{0},{1},0]'.format(end[0], end[1])


        ditancia = float(path[0][1])
        if ditancia > 1:
            meta = "{0:.2f}Km".format(ditancia)
        else:
            meta = "{0:.0f}m".format(ditancia*1000)


        context = { 'startOSM': startOSM[0], 'endOSM': endOSM[0], 'polyline' : hotline, 'maxGrade': max[0][0], 'meta' : meta,
                    'start': start, 'end': end}

        processTime = round(time.time() - start_time, 2)
        dataConvertida = int(datetime.now().date().strftime('%Y%m%d'))

        mensuredTemp = DateNode.create_or_update({'date': dataConvertida})
        mensured = mensuredTemp[0]

        metric = Metric(startPoint=start, endPoint=end, startId=startOSM[0][0], endId=endOSM[0][0], otimized=startOSM[0][1], metric=processTime, hour=time.strftime("%H:%M:%S") )
        metric.save()

        metricRel = metric.mensured.connect(mensured)

        db.commit()
    except Exception as e:
        db.rollback()
        context = {'meta': e}
    return render(request, 'paths/results.html', context)