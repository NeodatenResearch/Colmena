import random 
from Cliente import Cliente
from AlgoritmosAuxiliares import simularTasaDescuento 

# Función para aplicar un descuento a un cliente 
def aplicaDescuentoIndividual(cliente, a, b, producto_descuento): 
    tipos_descuento = ["VideoJuego", "Cupón", "Trivia", "Sorteo"]
    metodo = random.choice(tipos_descuento)
    # Vamos a simular si el cliente posee un método de descuento o no 
    tasa_descuento = simularTasaDescuento(a, b)
    # Caso en el que se puede aplicar el descuento
    if(random.random() < tasa_descuento):
        # Obtenemos el valor del descuento de forma aleatoria
        valor_descuento = simularTasaDescuento(a, b)
        # Agregamos el método de descuento al cliente
        cliente.agregarMetodoDescuento(producto_descuento, valor_descuento)
        return valor_descuento, metodo 
    return 0, None

# Función para ajustar el precio de un producto a medida que su demanda aumenta 
def ajusta_precio(precio, cantidad_nueva): 
    return precio * (1 - cantidad_nueva / 1000) 

