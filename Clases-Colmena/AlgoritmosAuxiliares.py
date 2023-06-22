import numpy as np
import random 
from Cliente import Cliente

# Algoritmo que simula la cantidad de clientes que solicitan un producto determinado
# en un periodo de tiempo determinado (utilizamos una variable aleatoria de Poisson)
'''
@param: lambda = tasa de llegada de clientes en un periodo de tiempo determinado
'''
def simularDemanda(lambda_):
    return np.random.poisson(lambda_)

# Función que simula si un cliente compra un producto o no (utilizamos una variable aleatoria de Bernoulli)
'''
@param: p = probabilidad de que un cliente compre un producto
'''
def simularCompra(p):
    return np.random.binomial(1, p)

# Función que simula la tasa con la que se darán descuentos a los clientes (utilizamos una beta con parámetros 0.5, 0.5)
def simularTasaDescuento(a, b):
    # Se puede ver como un descuento personalizado a medida que se simula de una distribución beta para cada cliente
    # Si los descuentos son estáticos, se modifica esta función para que de acuerdo a un diccionario regrese un valor predeterminado 
    return np.random.beta(a, b)

# Función para calcular el espacio del cargamento (se basa con la columna de productos_solicitados, peso y dimensiones)
def calculaEspacioCargamento(productos):
    espacio = 0
    peso_total = 0 
    for cantidad, peso, dimensiones in zip(productos['productos_solicitados'], productos['peso'], productos['dimensiones']):
        # Sumamos la cantidad de los productos por el volumen (dimensiones)
        espacio +=cantidad * dimensiones
        # Sumamos la cantidad de los productos por el peso
        peso_total += cantidad * peso
    return espacio, peso_total

# Algoritmos que simulan listas de clientes que compran productos
def simulaClientes(lambda_): 
    clientes = []
    for i in range(simularDemanda(lambda_)):
        clientes.append(Cliente(i, 'Cliente ' + str(i), 'Direccion ' + str(i), 'Telefono ' + str(i), np.random.randint(1, 5)))
    return clientes


# Función para calcular los ingresos por ventas considerando que se han aplicado descuentos por venta
# @param: dict (DESCUENTOS) para cada producto 
def calculaIngresosConDescuento(DESCUENTOS, productos):
    ingresos = 0 
    ingresos_por_producto = {}
    for producto, precio in zip(productos['Nombre'], productos['precio']):
        if(producto in DESCUENTOS):
            # Obtenemos los items que no tienen descuento 
            # Vamos a crear un vector de 1's de tamaño len(DESCUENTOS[producto])
            #                   precio_i * sum( (1- descuento_i)) * numero_self.DESCUENTOS_APLICADOS + items_sin_descuento * precio_i
            ingresos_producto = precio * sum(DESCUENTOS[producto])
            ingresos = ingresos + ingresos_producto
            ingresos_por_producto[producto] = ingresos_producto
        else: 
            # Raise error de que diseño 
            raise Exception("Error de diseño")

    return ingresos, ingresos_por_producto

