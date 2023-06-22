# Construcción del objeto producto
class Producto:
    def __init__(self, id_, nombre, precio, peso, dimensiones):
        self.id_ = id_
        self.nombre = nombre
        self.precio = precio
        self.peso = peso
        self.dimensiones = dimensiones
    
    def __str__(self):
        return 'Producto: ' + str(self.id_) + ' Nombre: ' + str(self.nombre) + ' Precio: ' + str(self.precio) + ' Peso: ' + str(self.peso) + ' Dimensiones: ' + str(self.dimensiones)
