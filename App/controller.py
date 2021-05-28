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
 """

import config as cf
import model
import csv
from DISClib.ADT import map as m
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import list as lt

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# ___________________________________________________


def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer


# Funciones para la carga de datos
def loadConnections(analyzer, connectionsfile):
    """
    Carga los datos de los archivos CSV en el modelo.
    Se crea un arco entre cada par de vertices que
    pertenecen a la misma conexión y van en el mismo sentido.

    addRouteConnection crea conexiones entre diferentes rutas
    servidas en una misma estación.
    """
    connectionsfile = cf.data_dir + connectionsfile
    input_file = csv.DictReader(open(connectionsfile, encoding="utf-8-sig"),
                                delimiter=",")
    lastconnection = None

    for connection in input_file:

        model.addStopConnection(analyzer, connection, connection)

    model.addRouteConnections(analyzer) #Conexiones locales 
    return analyzer


def loadCountries(analyzer, countriesfile):

    countriesfile = cf.data_dir + countriesfile
    input_file = csv.DictReader(open(countriesfile, encoding="utf-8-sig"),
                                delimiter=",") 

    capital_id = 24089

    for country in input_file:
        model.addCountryInfo(analyzer, country, capital_id)

        country["capital_id"] = capital_id

        capital_city = country["CapitalName"]
        analyzer = model.addCapitalasVertex(analyzer, capital_city, capital_id)

        #Se añade cada landing point a un mapa de hash determinado por el id del landing point
        info_map = analyzer["info_landing_id"]
        m.put(info_map, capital_id, country)

        #Se añade cada landing point a un mapa de hash determinado por el nombre de la ciudad del landing point
        info_map = analyzer["info_landing_name"]
        m.put(info_map, capital_city, country)

        capital_id += 1

    return analyzer

def createReferenceMaps(analyzer, capital_landing_points_file):

    capital_landing_points_file = cf.data_dir + capital_landing_points_file
    input_file = csv.DictReader(open(capital_landing_points_file, encoding="utf-8-sig"),
                                delimiter=",") 

    for city in input_file:

        city_info = city["name"].split(", ")

        city_country = city_info[-1]
        city_name = city_info[0]
        city_landing_point_id = int(city["landing_point_id"])

        
        #Se añade cada landing point a un mapa de hash determinado por el id del landing point
        info_map = analyzer["info_landing_id"]
        m.put(info_map, city_landing_point_id, city)

        #Se añade cada landing point a un mapa de hash determinado por el nombre de la ciudad del landing point
        info_map = analyzer["info_landing_name"]
        m.put(info_map, city_name, city)

    return analyzer



def loadCapitalVertex(analyzer, capital_landing_points_file):

    capital_landing_points_file = cf.data_dir + capital_landing_points_file
    input_file = csv.DictReader(open(capital_landing_points_file, encoding="utf-8-sig"),
                                delimiter=",") 

    for city in input_file:
        

        city_info = city["name"].split(", ")

        city_country = city_info[-1]
        city_name = city_info[0]
        city_landing_point_id = int(city["landing_point_id"])
    
        if m.contains(analyzer["countries"], city_country):

            entry = m.get(analyzer["countries"], city_country)
            capital_info = me.getValue(entry)

            model.addConnectiontoCapitalVertex(analyzer, capital_info, city)

    return analyzer


def getMST(analyzer):

    return model.getMST(analyzer)    


# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo
def totalLandingPoints(analyzer):
    """
    Total de paradas de landing points
    """
    return model.totalLandingPointss(analyzer)


def totalConnections(analyzer):
    """
    Total de enlaces entre vertices
    """
    return model.totalConnections(analyzer)


def totalCountries(analyzer):

    return model.totalCountries(analyzer)

def getLandingPointPos(analyzer, pos):

    return model.getLandingPointPos(analyzer, pos)

def getCountryPos(analyzer, pos):

    return model.getCountryPos(analyzer, pos)


def getCluster(analyzer):

    return model.getCluster(analyzer)

def getClusterSize(cluster):

    return model.getClusterSize(cluster)


def getStronglyConnected(analyzer, cluster, landing_point_1, landing_point_2):
    vertex_map = analyzer["landing_points"]
    names_map = analyzer["info_landing_name"]

    #Se accede al mapa cuyas llaves son los nombres para obtener el id correspondiente al landing_point
    landing_point_1_id = me.getValue(m.get(names_map, landing_point_1))["landing_point_id"]
    landing_point_2_id = me.getValue(m.get(names_map, landing_point_2))["landing_point_id"]

    #Una vez se ha obtenido el id, se accede al mapa con los landing_points y sus respectivos cables
    landing_point_1_vertices_entry = m.get(vertex_map, landing_point_1_id)
    landing_point_2_vertices_entry = m.get(vertex_map, landing_point_2_id)

    #Se obtiene una lista con los cables
    landing_point_1_vertices_lst = me.getValue(landing_point_1_vertices_entry)
    landing_point_2_vertices_lst = me.getValue(landing_point_2_vertices_entry)

    #Mediante la iteración de todos los cables (tanto landing_point_1 como landing_point_2) es posible encontrar los
    #vértices relacionados a esta búsqueda.
    for landing_point_A in lt.iterator(landing_point_1_vertices_lst):
        for landing_point_B in lt.iterator(landing_point_2_vertices_lst):

            #Se evalua si ambos landing_points se encuentran conectados por el mismo cable (de lo contrario no hay conexión)
            if landing_point_A == landing_point_B:

                complete_landing_point_1 = "{}-{}".format(landing_point_1_id, landing_point_A)
                complete_landing_point_2 = "{}-{}".format(landing_point_2_id, landing_point_B)

                cluster_check = model.getStronglyConnected(analyzer, cluster, complete_landing_point_1, complete_landing_point_2)

                if cluster_check == True:

                    return cluster_check

def getLandingPointConnections(analyzer):

    return model.getLandingPointConnections(analyzer)


def minimumCountryRoute(analyzer, country_A, country_B):

    return model.minimumCountryRoute(analyzer, country_A, country_B)



def getAdjacentVertices(analyzer, landing_point):

    return model.getAdjacentVertices(analyzer, landing_point)

def getAdjacentCountries(analyzer, adjacent_vertices):

    return model.getAdjacentCountries(analyzer, adjacent_vertices)