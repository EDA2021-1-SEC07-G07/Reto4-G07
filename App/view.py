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
    analyzer = controller.loadConnections(analyzer, connectionsfile) #Se crea el grafo principal con conexiones locales y remotas (submarinas)

    analyzer = controller.loadCountries(analyzer, countriesfile) #Se crea un mapa de hash con los paises y se genera un vértice terrestre por capital

    analyzer = controller.loadCapitalVertex(analyzer, capital_landing_points_file)#Se crean las conexiones entre el vertice capital y las diferentes ciudades

    numedges = controller.totalConnections(analyzer)
    numvertex = controller.totalLandingPoints(analyzer)
    numcountries = controller.totalCountries(analyzer)
    first_landing_point = controller.getLandingPointPos(analyzer, 1)
    last_country_info = controller.getCountryPos(analyzer, -1)

    name = last_country_info["CountryName"]
    population = last_country_info["Population"]
    internet_users = last_country_info["Internet users"]

    print('Numero de Landing Points: ' + str(numvertex))
    print('Numero de arcos (conexiones entre Landing Points): ' + str(numedges))
    print("El número total de paises cargados: " + str(numcountries))
    print("El primer landing point cargado es: " + str(first_landing_point))
    print("último país cargado: Nombre: {}, Población: {}, Usuarios en internet: {}.".format(name, population, internet_users))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))
    


def optionThree(analyzer):
    
    cluster = controller.getCluster(analyzer)
    
    cluster_number = controller.getClusterSize(cluster)

    landing_point_1 = input("Ingrese el nombre del primer landing point que desea evaluar: ")
    landing_point_2 = input("Ingrese el nombre del segundo landing point que desea evaluar: ")

    strongly_connected_landing_points = controller.getStronglyConnected(analyzer, cluster, landing_point_1, landing_point_2)

    if strongly_connected_landing_points == True:
        strongly_connected_landing_points = "SÍ."

    else:
        strongly_connected_landing_points = "NO."

    print("\nEl número total de clusters en la red es de: {}".format(cluster_number))
    print("¿El landing point {} y el landing point {} están en el mismo cluster? {}".format(landing_point_1, landing_point_2, strongly_connected_landing_points))



def optionFour(analyzer, initialStation):
    pass

def optionFive(analyzer, destStation):
    pass

def optionSix(analyzer, destStation):
    pass

def optionSeven(analyzer):
    pass

def optionEight(analyzer):
    pass

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


        else:
            sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()
