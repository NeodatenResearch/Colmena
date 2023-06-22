# Construcción del objeto cliente
class Cliente:
    def __init__(self, id_, nombre, direccion, telefono, cluster):
        self.id_ = id_
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        # clave (id del producto): value (cantidad de productos) 
        self.productos = {}
        self.cluster = cluster 
        # key (id del producto en descuento): value (valor del descuento)
        self.METODOS_DESCUENTO = {}
    
    # Método que agrega un producto al cliente
    def agregarProducto(self, producto, cantidad):
        if(producto in self.productos):
            self.productos[producto] += cantidad
        else: 
            self.productos[producto] = cantidad
    
    # Método que agrega un método de descuento al cliente
    def agregarMetodoDescuento(self, id, valor):
        if(id in self.productos): 
            self.METODOS_DESCUENTO[id] = valor
    
    def __str__(self):
        return 'Cliente: ' + str(self.id_) + ' Nombre: ' + str(self.nombre) + ' Productos: ' + str(self.productos) + ' Métodos de descuento: ' + str(self.METODOS_DESCUENTO)