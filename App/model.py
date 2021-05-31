"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.ADT import indexminpq as pq
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import prim
from DISClib.Utils import error as error
from DISClib.DataStructures import mapentry as me
from DISClib.DataStructures import bst 
from DISClib.DataStructures import rbt
from DISClib.DataStructures import indexheap as iheap
from math import radians, cos, sin, asin, sqrt
from DISClib.Algorithms.Sorting import mergesort 
import random
assert config

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def newAnalyzer():
    """ Inicializa el analizador

   landing_points: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre landing points
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'landing_points': None,
                    'connections': None,
                    'components': None,
                    'paths': None,
                    "countries": None,
                    "capital_landing_point":None,
                    "info_landing_id": None,
                    "info_landing_name": None
                    }

        analyzer['landing_points'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareLandingPointIds)

        analyzer['countries'] = m.newMap(numelements=260,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)         

        analyzer['info_landing_id'] = m.newMap(numelements=260,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)


        analyzer['info_landing_name'] = m.newMap(numelements=260,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)   
   


        return analyzer

    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')



# Funciones para agregar informacion al catalogo
def addStopConnection(analyzer, lastconnection, connection):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        origin = formatOriginVertex(lastconnection)
        destination = formatDestinationVertex(connection)

        cleanConnectionDistance(lastconnection, connection)

        origin_landing_point = int(origin.split("-")[0])
        destination_landing_point = int(destination.split("-")[0])

        origin_latitude = float(me.getValue(m.get(analyzer["info_landing_id"], origin_landing_point))["latitude"])
        origin_longitude = float(me.getValue(m.get(analyzer["info_landing_id"], origin_landing_point))["longitude"])

        destination_latitude = float(me.getValue(m.get(analyzer["info_landing_id"], destination_landing_point))["latitude"])
        destination_longitude = float(me.getValue(m.get(analyzer["info_landing_id"], destination_landing_point))["longitude"])

        distance = haversine(origin_latitude, origin_longitude, destination_latitude, destination_longitude)

        addLandingPoint(analyzer, origin)
        addLandingPoint(analyzer, destination)
        addConnection(analyzer, origin, destination, distance)
        addCableLandingPoint(analyzer, connection)
        addCableLandingPoint(analyzer, lastconnection)
        return analyzer

    except Exception as exp:
        error.reraise(exp, 'model:addStopConnection')


def addLandingPoint(analyzer, landing_point_id):
    """
    Adiciona un landing_point como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['connections'], landing_point_id):
            gr.insertVertex(analyzer['connections'], landing_point_id)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addstop')


def addConnection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, distance)
    return analyzer


def addCableLandingPoint(analyzer, connection):
    """
    Agrega a un landing point, un cable que es utilizado en ese vertice
    """
    entry = m.get(analyzer['landing_points'], connection['destination'])
    if entry is None:
        lstroutes = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstroutes, connection['cable_id'])
        m.put(analyzer['landing_points'], connection['destination'], lstroutes)


    else:
        lstroutes = entry['value']
        info = connection['cable_id']
        if not lt.isPresent(lstroutes, info):
            lt.addLast(lstroutes, info)
    return analyzer


def addRouteConnections(analyzer):
    """
    Por cada vertice (cada estacion) se recorre la lista
    de rutas servidas en dicha estación y se crean
    arcos entre ellas para representar el cambio de ruta
    que se puede realizar en una estación.
    """
    lststops = m.keySet(analyzer['landing_points'])
    for key in lt.iterator(lststops):
        lstroutes = m.get(analyzer['landing_points'], key)['value']
        prevrout = None
        for route in lt.iterator(lstroutes):
            route = key + '-' + route
            if prevrout is not None:

                local_distance = 0.1

                addConnection(analyzer, prevrout, route, local_distance)
                addConnection(analyzer, route, prevrout, local_distance)
            prevrout = route



def addCountryInfo(analyzer, country, capital_id):

    country_name = country["CountryName"]

    m.put(analyzer["countries"], country_name, country)



def addCapitalasVertex(analyzer, capital, capital_id):

    graph = analyzer["connections"]
    capital_id = str(capital_id)

    gr.insertVertex(graph, capital_id)

    return analyzer



def addConnectiontoCapitalVertex(analyzer, capital_info, city):

    graph = analyzer["connections"]

    city_landing_point_id = city["landing_point_id"]
    capital_name = capital_info["CapitalName"]
    capital_id = str(capital_info["capital_id"])

    capital_lat = float(capital_info["CapitalLatitude"])
    capital_long = float(capital_info["CapitalLongitude"])

    city_lat = float(city["latitude"])
    city_lon = float(city["longitude"])

    #Se aplica la fórmula de haversine para encontrar la distancia entre la capital y sus ciudades
    distance = haversine(capital_lat, capital_long, city_lat, city_lon)

    if m.contains(analyzer["landing_points"], city_landing_point_id):

        entry = m.get(analyzer["landing_points"], city_landing_point_id)
        cable_list = me.getValue(entry)

        for cable in lt.iterator(cable_list):

            vertex = city_landing_point_id + "-" + cable

            gr.addEdge(graph, capital_id, vertex, distance)

            gr.addEdge(graph, vertex, capital_id, distance)


            #Se añade el cable de conexión
            entry = m.get(analyzer['landing_points'], capital_id)
            if entry is None:
                lstroutes = lt.newList(cmpfunction=compareroutes)
                lt.addLast(lstroutes, cable)
                m.put(analyzer['landing_points'], capital_id, lstroutes)
            else:
                lstroutes = entry['value']
                info = cable
                if not lt.isPresent(lstroutes, info):
                    lt.addLast(lstroutes, info)


# Funciones para creacion de datos

# Funciones de consulta
def totalLandingPointss(analyzer):
    """
    Retorna el total de landing points (vertices) del grafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['connections'])


def totalCountries(analyzer):

    return m.size(analyzer["countries"])


def getLandingPointPos(analyzer, pos):

    graph = analyzer["connections"]

    vertex_list = gr.vertices(graph)

    vertex = lt.getElement(vertex_list, pos)

    vertex_landing_point = int(vertex.split("-")[0])

    vertex_map = analyzer["info_landing_id"]

    landing_point_info = m.get(vertex_map, vertex_landing_point)

    return landing_point_info


def getCountryPos(analyzer, pos):

    country_map = analyzer["countries"]
    last_element = None

    #Si pos es igual a -1, se busca el último vértice 
    if pos == -1:    
        
        country_list = m.valueSet(analyzer["countries"])

        last_country = lt.lastElement(country_list)

    return last_country


def getCluster(analyzer):

    cluster_data = scc.KosarajuSCC(analyzer["connections"])

    return cluster_data


def getClusterSize(cluster):

    cluster_number = scc.connectedComponents(cluster)
    return cluster_number

def getStronglyConnected(analyzer, cluster, landing_point_1, landing_point_2):

    strongly_connected = scc.stronglyConnected(cluster, landing_point_1, landing_point_2)

    return strongly_connected



def getLandingPointConnections(analyzer):

    vertex_map = analyzer["landing_points"]
    vertex_list = m.keySet(vertex_map)
    landing_point_list = lt.newList(datastructure = "ARRAY_LIST")
    
    for vertex_key in lt.iterator(vertex_list):

        temp_list = lt.newList(datastructure = "ARRAY_LIST")
        vertex_value = lt.size(me.getValue(m.get(vertex_map, vertex_key)))

        lt.addLast(temp_list, vertex_key)
        lt.addLast(temp_list, vertex_value)

        lt.addLast(landing_point_list, temp_list)

    sorted_vertex_list = mergesort.sort(landing_point_list, cmpnumberofcables)
    
    top_10_vertex_list = lt.subList(sorted_vertex_list, 1, 10)
    top_10_vertex_list_final = lt.newList(datastructure = "ARRAY_LIST")

    for top_vertex in lt.iterator(top_10_vertex_list):

        top_vertex_id = int(lt.getElement(top_vertex, 1))

        top_vertex_info = me.getValue(m.get(analyzer["info_landing_id"], top_vertex_id))
        top_vertex_info["connected_cables"] = lt.getElement(top_vertex, 2)

        lt.addLast(top_10_vertex_list_final, top_vertex_info)

    #SE RETORNA UNA LISTA (TIPO LST) QUE CONTIENE 10 DICCIONARIOS
    return top_10_vertex_list_final






def minimumCountryRoute(analyzer, country_A, country_B):

    graph = analyzer["connections"]
    country_map = analyzer["countries"]
    capital_name_map = analyzer["info_landing_id"]

    capital_city_A_vertex = str(me.getValue(m.get(country_map, country_A))["capital_id"])
    capital_city_B_vertex = str(me.getValue(m.get(country_map, country_B))["capital_id"])

    dijkstra_search = djk.Dijkstra(graph, capital_city_A_vertex)

    if djk.hasPathTo(dijkstra_search, capital_city_B_vertex):

        dijkstra_cost = djk.distTo(dijkstra_search, capital_city_B_vertex)
        dijkstra_route = djk.pathTo(dijkstra_search, capital_city_B_vertex)
        
        return (dijkstra_cost, dijkstra_route)

    else:

        return None


def getMST(analyzer):



    vertex_list = m.keySet(analyzer["landing_points"])
    vertex_amount = lt.size(vertex_list)

    random_number = random.randrange(1, vertex_amount)
    random_vertex_key = lt.getElement(vertex_list, random_number)
    random_vertex_value = lt.firstElement(me.getValue(m.get(analyzer["landing_points"], random_vertex_key)))

    random_vertex = "{}-{}".format(random_vertex_key, random_vertex_value)

 
    MST = prim.PrimMST(analyzer["connections"])
    MST_tree = MST["mst"]

    MST_weight = prim.weightMST(analyzer["connections"], MST)
    MST_connected_nodes = MST_tree["size"]
    MST_largest_branch = MST_connected_nodes - 1

    #TODO 
    return (MST_weight, MST_connected_nodes, MST_largest_branch)


def getAdjacentVertices(analyzer, landing_point):

    graph = analyzer["connections"]

    landing_point_id = me.getValue(m.get(analyzer["info_landing_name"], landing_point))["landing_point_id"]

    vertex_list = me.getValue(m.get(analyzer["landing_points"], landing_point_id))

    adjacent_list = lt.newList(datastructure = "ARRAY_LIST")

    for vertex in lt.iterator(vertex_list):

        vertex_name = landing_point_id + "-" + vertex

        temp_list = gr.adjacents(graph, vertex_name)

        lt.addLast(adjacent_list, temp_list)

    return adjacent_list


def getAdjacentCountries(analyzer, adjacent_vertices, landing_point):

    landing_map = analyzer["info_landing_id"]

    landing_map_name = analyzer["info_landing_name"]

    adjacent_countries = m.newMap(numelements=260,
                                     maptype='PROBING')

    adjacent_countries_list = lt.newList(datastructure = "ARRAY_LIST")


    for cable in lt.iterator(adjacent_vertices):

        for vertex in lt.iterator(cable):

            adjacent_landing = int(vertex.split("-")[0])

            adjacent_info = me.getValue(m.get(landing_map, adjacent_landing))

            if "name" in adjacent_info.keys():
                #Then the adjacent cable belongs to a normal city
                adjacent_country = adjacent_info["name"].split(", ")[-1]

            else:
                #The cable is connected to a capital
                adjacent_country = adjacent_info["CountryName"]

            if not m.contains(adjacent_countries, adjacent_country):

                actual_landing_point_lat = float(me.getValue(m.get(landing_map_name, landing_point))["latitude"])
                actual_landing_point_lon = float(me.getValue(m.get(landing_map_name, landing_point))["longitude"])

                adjacent_country_lat = float(me.getValue(m.get(analyzer["countries"], adjacent_country))["CapitalLatitude"])
                adjacent_countries_lon = float(me.getValue(m.get(analyzer["countries"], adjacent_country))["CapitalLongitude"])

                adjacent_country_distance = haversine(actual_landing_point_lat, actual_landing_point_lon, adjacent_country_lat, adjacent_countries_lon)

                m.put(adjacent_countries, adjacent_country, adjacent_country_distance)

    
    for key in lt.iterator(m.keySet(adjacent_countries)):

        value = me.getValue(m.get(adjacent_countries, key))

        mini_list = lt.newList(datastructure = "ARRAY_LIST")
        lt.addLast(mini_list, key)
        lt.addLast(mini_list, value)

        lt.addLast(adjacent_countries_list, mini_list)

    
    return adjacent_countries_list
            




def sortAdjacentCountries(adjacent_countries):

    sorted_list = mergesort.sort(adjacent_countries, cmpCountriesDist)

    return sorted_list




# Funciones utilizadas para comparar elementos dentro de una lista

def cmpnumberofcables(vertex_1, vertex_2):

    size_1 = lt.getElement(vertex_1, 2)
    size_2 = lt.getElement(vertex_2, 2)

    if size_1 > size_2:

        return True

    else:
        return False

    



# Funciones de ordenamiento

def compareLandingPointIds(landing_point, keylandingpoint):
    """
    Compara dos estaciones
    """
    landing_id = keylandingpoint['key']
    if (landing_point == landing_id):
        return 0
    elif (landing_point > landing_id):
        return 1
    else:
        return -1

def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1

def cmpCountriesDist(country_1, country_2):

    country_dist_1 = lt.getElement(country_1, 2)
    country_dist_2 =  lt.getElement(country_2, 2)

    if country_dist_1 > country_dist_2:
        return True

    else:
        return False

# Funciones de ayuda 
def formatOriginVertex(connection):
    """
    Se formatea el nombrer del vertice con el id del landing point seguido del cable específico
    """
    name = connection['origin'] + '-'
    name = name + connection['cable_id']
    return name

def formatDestinationVertex(connection):
    """
    Se formatea el nombrer del vertice con el id del landing point seguido del cable específico
    """
    name = connection['destination'] + '-'
    name = name + connection['cable_id']
    return name


def cleanConnectionDistance(lastconnection, connection):
    """
    En caso de que el archivo tenga un espacio en la
    distancia, se reemplaza con cero.
    """
    if connection['cable_length'] == 'n.a.':
        connection['cable_length'] = "0"
    if lastconnection['cable_length'] == 'n.a.':
        lastconnection['cable_length'] = "0"

def haversine(lat1, lon1, lat2, lon2):
    """Función para calcular la distancia entre dos coordenadas. Tomada del usuario https://stackoverflow.com/users/7887334/clay"""
    R = 6372.8 #For Earth radius in kilometers use 6372.8 km
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))

    return R * c



