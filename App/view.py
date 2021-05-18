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


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""
connectionsfile = "connections.csv"

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
    controller.loadServices(analyzer, connectionsfile)

def optionThree(analyzer):
    pass

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


        else:
            sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()
