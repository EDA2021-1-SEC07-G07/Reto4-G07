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
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error

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
                    'paths': None
                    }

        analyzer['landing_points'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
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

        cable_length = connection['cable_length'].split()[0].replace(",","")

        distance = float(cable_length)

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
# Funciones para creacion de datos

# Funciones de consulta

# Funciones utilizadas para comparar elementos dentro de una lista

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