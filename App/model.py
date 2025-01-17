﻿"""
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
import ipapi
import folium
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

        analyzer["info_cable_name"] = m.newMap(numelements=260,
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

        ########## MAPA DE CABLES USADO EN EL REQ 6 ##############
        cable_mini_list = lt.newList("ARRAY_LIST")
        lt.addLast(cable_mini_list, connection["cable_id"])
        lt.addLast(cable_mini_list, connection["capacityTBPS"])

        m.put(analyzer["info_cable_name"], connection["cable_name"], cable_mini_list)
        #########################################################


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
            



def getMaxBandwidthCountry(analyzer, country_name, cable_name):

    adjacent_max_bandwidth_country_map = m.newMap(numelements=17,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

    capital_name = me.getValue(m.get(analyzer["countries"], country_name))["CapitalName"]
    capital_landing_point_id = me.getValue(m.get(analyzer["info_landing_name"], capital_name))["capital_id"]

    host_vertex_lp = str(capital_landing_point_id) 
    
    adjacent_internal_vertices = gr.adjacents(analyzer["connections"], host_vertex_lp)

    #Se encuentra el nombre interno del cable (con el que se forma el vértice con base en su nombre real)
    if m.contains(analyzer["info_cable_name"], cable_name):
        cable_id = lt.getElement(me.getValue(m.get(analyzer["info_cable_name"], cable_name)), 1)
        cable_bandwidth = lt.getElement(me.getValue(m.get(analyzer["info_cable_name"], cable_name)), 2).replace(".", "")
    

    for internal_vertex in lt.iterator(adjacent_internal_vertices):
        if cable_id in internal_vertex:
          
            adjacent_external_vertices = gr.adjacents(analyzer["connections"], internal_vertex)

            for external_vertex in lt.iterator(adjacent_external_vertices):

                extra_vertices = gr.adjacents(analyzer["connections"], external_vertex)

                for vertex in lt.iterator(extra_vertices):

                    try:
                        #En dado caso que sea un país externo, no hay error
                        landing_point_id = int(vertex.split("-")[0])
                        adjacent_vertex = me.getValue(m.get(analyzer["info_landing_id"], landing_point_id))

                        if adjacent_vertex["name"].split(", ")[-1] != country_name:

                            adjacent_country = adjacent_vertex["name"].split(", ")[-1]
                            adjacent_country_internet_users = me.getValue(m.get(analyzer["countries"], adjacent_country))["Internet users"].replace(".", "")

                            adjacent_country_max_bandwith = (float(cable_bandwidth) / float(adjacent_country_internet_users))*10000

                            m.put(adjacent_max_bandwidth_country_map, adjacent_country, adjacent_country_max_bandwith)

                    except:
                        #En dado caso que se haga referencia al mismo país (adjacente interno) se da un error que es ignorado
                        pass


    return adjacent_max_bandwidth_country_map


def getIPInfo(ip):

    return ipapi.location(ip)




def getClosestLPtoIP(analyzer, ip_info):

    ip_latitude = ip_info["latitude"]
    ip_longitude = ip_info["longitude"]
    previous_hav_distance = -1
    closest_LP = None

    #Jump to the Capital City 
    ip_country = ip_info["country_name"]
    ip_capital = me.getValue(m.get(analyzer["countries"], ip_country))["CapitalName"]

    closest_LP = me.getValue(m.get(analyzer["info_landing_name"], ip_capital))["capital_id"]

    return closest_LP


def getMinimumRouteLP(analyzer, ip_1_closest_lp, ip_2_closest_lp):

    graph = analyzer["connections"]

    dijkstra_search = djk.Dijkstra(graph, ip_1_closest_lp)

    if djk.hasPathTo(dijkstra_search, ip_2_closest_lp):

        dijkstra_route = djk.pathTo(dijkstra_search, ip_2_closest_lp)
        dijstra_jumps = lt.size(dijkstra_route)
        
        return (dijkstra_route, dijstra_jumps)

    else:

        return None


def graphSubmarineMap(analyzer):

    graph = analyzer["connections"]

    gm = folium.Map(location=[4.6012, -74.065], zoom_start=3, tiles="Stamen Terrain")

    vertex_list = gr.vertices(graph)
    edge_list = gr.edges(graph)

    for vertex in lt.iterator(vertex_list):

        landing_point = int(vertex.split("-")[0])
        landing_point_info = me.getValue(m.get(analyzer["info_landing_id"], landing_point))
        
        if landing_point < 24089:
            #Se trata de un landing point submarino
            landing_point_latitude = landing_point_info["latitude"]
            landing_point_longitude = landing_point_info["longitude"]

            landing_point_name = landing_point_info["name"]
            tooltip = "Click me!"

            folium.Marker(
                [landing_point_latitude, landing_point_longitude], popup="<i>{}</i>".format(landing_point_name), tooltip=tooltip,
                icon=folium.Icon(color="blue")
            ).add_to(gm)
        
        else:
            #Se trata de un landing point terreste de capital
            landing_point_latitude = landing_point_info["CapitalLatitude"]
            landing_point_longitude = landing_point_info["CapitalLongitude"]

            landing_point_name = landing_point_info["CapitalName"] + ", " + landing_point_info["CountryName"]
            tooltip = "Click me!"

            if landing_point_latitude != "":

                folium.Marker(
                    [landing_point_latitude, landing_point_longitude], popup="<i>{}</i>".format(landing_point_name), tooltip=tooltip,
                    icon=folium.Icon(color="red")
                ).add_to(gm)

    for edge in lt.iterator(edge_list): 

        vertexA = edge["vertexA"]
        vertexB = edge["vertexB"]

        landing_point_A = int(vertexA.split("-")[0])
        landing_point_A_info = me.getValue(m.get(analyzer["info_landing_id"], landing_point_A))
        cable_id_A = "-".join((vertexA.split("-")[1:-1]))

        landing_point_B = int(vertexB.split("-")[0])
        landing_point_B_info = me.getValue(m.get(analyzer["info_landing_id"], landing_point_B))
        cable_id_B = "-".join((vertexB.split("-")[1:-1]))


        if landing_point_A < 24089:
            #Se trata de un landing point submarino
            landing_point_A_latitude = landing_point_A_info["latitude"]
            landing_point_A_longitude = landing_point_A_info["longitude"]

        else:
            #Se trata de un landing point terreste de capital
            landing_point_A_latitude = landing_point_A_info["CapitalLatitude"]
            landing_point_A_longitude = landing_point_A_info["CapitalLongitude"]

        if landing_point_B < 24089:
            #Se trata de un landing point submarino
            landing_point_B_latitude = landing_point_B_info["latitude"]
            landing_point_B_longitude = landing_point_B_info["longitude"]

        else:
            #Se trata de un landing point terreste de capital
            landing_point_B_latitude = landing_point_B_info["CapitalLatitude"]
            landing_point_B_longitude = landing_point_B_info["CapitalLongitude"]


        coordinates = [[float(landing_point_A_latitude), float(landing_point_A_longitude)], 
                   [float(landing_point_B_latitude), float(landing_point_B_latitude)]]

        if landing_point_A_latitude != "" and landing_point_B_latitude != "":
            folium.PolyLine(coordinates, color='green', opacity = 0.3).add_to(gm)

    gm.save("./Data/map.html")

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




def sortAdjacentCountries(adjacent_countries):

    sorted_list = mergesort.sort(adjacent_countries, cmpCountriesDist)

    return sorted_list




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



