"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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

import sys
import config
import threading
from App import controller
from DISClib.ADT import stack
assert config
import time

from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""
connectionsfile = "connections.csv"
countriesfile = "countries.csv"
capital_landing_points_file = "landing_points.csv"

def printMenu():
    print("Bienvenido")
    print("1- Inicializar analizador")
    print("2- Cargar información de cables submarinos")
    print("3- Identificar los clústeres de comunicación (Req-1)")
    print("4- Identificar los puntos de conexión críticos de la red (Req-2)")
    print("5- Identificar la ruta de menor distancia (Req-3)")
    print("6- Identificar la infraestructura crítica de la red (Req-4)")
    print("7- Análisis de fallas (Req-5)")
    print("8- Los mejores canales para transmitir (Req-6)")
    print("9- La mejor ruta para comunicarme (Req-7)")
    print("10- Graficando los grafos (Req-8)")


def optionTwo(analyzer):

    print("\nCargando información de cables submarinos ....")

    analyzer = controller.createReferenceMaps(analyzer, capital_landing_points_file)

    analyzer = controller.loadConnections(analyzer, connectionsfile) #Se crea el grafo principal con conexiones locales y remotas (submarinas)

    analyzer = controller.loadCountries(analyzer, countriesfile) #Se crea un mapa de hash con los paises y se genera un vértice terrestre por capital

    analyzer = controller.loadCapitalVertex(analyzer, capital_landing_points_file)#Se crean las conexiones entre el vertice capital y las diferentes ciudades


    numedges = controller.totalConnections(analyzer) #Se obtiene el número total de arcos
    numvertex = controller.totalLandingPoints(analyzer) #Se obtiene el número total de vértices
    numcountries = controller.totalCountries(analyzer) #Se obtiene el número total de paises con cables registrados en el grafo
    first_landing_point = controller.getLandingPointPos(analyzer, 1) #Se obtiene la información del primer landing point
    last_country_info = controller.getCountryPos(analyzer, -1) #Se obtiene la información del último landing point cargado

    name = last_country_info["CountryName"]
    population = last_country_info["Population"]
    internet_users = last_country_info["Internet users"]

    print('Numero de Landing Points: ' + str(numvertex))
    print('Numero de arcos (conexiones entre Landing Points): ' + str(numedges))
    print("El número total de paises cargados: " + str(numcountries))
    print("El primer landing point cargado es: " + str(first_landing_point)) #TODO FORMATEAR PRINT!
    print("último país cargado: Nombre: {}, Población: {}, Usuarios en internet: {}.".format(name, population, internet_users))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))
    


def optionThree(analyzer):
    
    #En primera instancia, se obtiene una estructura que diferencia los componentes fuertemente conectados (clusters)
    cluster = controller.getCluster(analyzer)
    
    #Se obtiene el número de clusters dentro de la estructura ya obtenida
    cluster_number = controller.getClusterSize(cluster)

    landing_point_1 = input("Ingrese el nombre del primer landing point que desea evaluar: ")
    landing_point_2 = input("Ingrese el nombre del segundo landing point que desea evaluar: ")

    #Se evalua si los landing_points ingresados están conectados en el mismo cluster
    strongly_connected_landing_points = controller.getStronglyConnected(analyzer, cluster, landing_point_1, landing_point_2)

    if strongly_connected_landing_points == True:
        strongly_connected_landing_points = "SÍ."

    else:
        strongly_connected_landing_points = "NO."

    print("\nEl número total de clusters en la red es de: {}".format(cluster_number))
    print("¿El landing point {} y el landing point {} están en el mismo cluster? {}".format(landing_point_1, landing_point_2, strongly_connected_landing_points))



def optionFour(analyzer):
    
    interconnected_landing_points = controller.getLandingPointConnections(analyzer)
    print(interconnected_landing_points)#TODO FORMATEAR PRINT!

def optionFive(analyzer):
    
    country_A = input("Ingrese el país desde el que desea encontrar la ruta mínima: ")
    country_B = input("Ingrese el país hasta el que desea encontrar la ruta mínima: ")

    dijkstra_info = controller.minimumCountryRoute(analyzer, country_A, country_B)

    minimum_total_distance = dijkstra_info[0]
    minimum_route = dijkstra_info[1]

    #TODO-FORMATEAR PRINT!
    print(minimum_total_distance)
    print(minimum_route)

def optionSix(analyzer):
    
    minimum_spanning_tree = controller.getMST(analyzer)
    print(minimum_spanning_tree) #TODO - FORMATEAR PRINT!

def optionSeven(analyzer):
    
    landing_point = input("Ingrese el nombre del landing point respecto al cual quiere determinar los efectos de su fallo: ")

    adjacent_vertices = controller.getAdjacentVertices(analyzer, landing_point)

    adjacent_countries = controller.getAdjacentCountries(analyzer, adjacent_vertices, landing_point)

    sorted_adjacent_countries = controller.sortAdjacentCountries(adjacent_countries)

    print(sorted_adjacent_countries) #TODO-FORMATEAR PRINT!


def optionEight(analyzer):
    country_name = input("Ingrese el nombre del país desde el que inicia el cable: ")
    cable_name = input("Ingrese el nombre del cable: ")

    max_bandwidth_country_map = controller.getMaxBandwidthCountry(analyzer, country_name, cable_name)

    print(max_bandwidth_country_map)#TODO - FORMATEAR PRINT!

def optionNine(analyzer):
    pass

def optionTen(analyzer):
    pass


"""
Menu principal
"""

def thread_cycle():
    while True:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n>')

        if int(inputs[0]) == 1:
            print("\nInicializando....")
            # cont es el controlador que se usará de acá en adelante
            analyzer = controller.init()

        elif int(inputs[0]) == 2:
            optionTwo(analyzer)

        elif int(inputs[0]) == 3:
            optionThree(analyzer)

        elif int(inputs[0]) == 4:
            optionFour(analyzer)

        elif int(inputs[0]) == 5:
            optionFive(analyzer)

        elif int(inputs[0]) == 6:
            optionSix(analyzer)

        elif int(inputs[0]) == 7:
            optionSeven(analyzer)

        elif int(inputs[0]) == 8:
            optionEight(analyzer)


        else:
            sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()
