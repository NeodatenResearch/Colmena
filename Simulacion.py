import numpy as np
import pandas as pd
import random
import plotly.graph_objects as go
from Cliente import Cliente
from Producto import Producto
from AlgoritmosAuxiliares import simulaClientes, calculaEspacioCargamento, simularDemanda, calculaIngresosConDescuento
from Colmena import ajusta_precio, aplicaDescuentoIndividual
from IPython.display import display

'''
Clase que emula la simulación del worflow de Colmena 
'''
class Simulacion: 
    # Constructor de la clase de Simulación 
    def __init__(self, query):
        
        # (INT) Tasa de clientes que están utilizando la aplicación 
        self.tasa_clientes_compran = query["tasa_clientes_compran"]
        # (INT) Parámetros para el descuento 
        self.forma_a = query["forma_a"]
        self.forma_b = query["forma_b"]
        # (Dict) Diccionario que indica la cantidad promedio de consumo por producto
        self.cantidad_promedio = query["cantidad_promedio"] 
        # (INT) Tasa de clientes a la que puedes llegar a través de publicidad en un intervalo de tiempo (1 minuto, por ejemplo)
        self.tasa_clientes_compran_nuevos = query["tasa_clientes_compran_nuevos"] 
        # (Dict) Diccionario que indica la tasa con la que nuevos clientes demandan por producto
        self.tasas_nuevos_clientes = query["tasas_nuevos_clientes"] 
        # (INT) Tiempo de simulación (en minutos)
        self.tiempo = query["tiempo"] 
        # (INT) Tasa de clientes a la que se podrá alcanzar por medio de publicidad en el intervalo de tiempo (variable de arriba)
        self.tasa_tota_nuevos_clientes = query["tasa_tota_nuevos_clientes"] 
        # (Dict) Límite inferior del precio del producto 
        self.limites_inferiores = query["limites_inferiores"]
        # Dataframe que contiene los productos
        self.productos = query["productos"]

        # Estructura que contiene los precios ajustados con los descuentos
        self.DESCUENTOS_APLICADOS = {}
        # Estructura que contiene la cantidad solicitada por producto 
        self.CANTIDADES_SOLICITADAS = {}
        # Estructura que contiene la cantidad por producto que fue demandado y que no se pudo satisfacer (por agotamiento de inventario)
        self.CANTIDADES_NO_SATISFECHAS = {}
        # Estructura que cuenta los métodos de descuento utilizados 
        self.METODOS_DESCUENTO = {}

    # Método que simula la cantidad de clientes que están utilizando la aplicación antes de la simulación dinámica 
    # @param tiempo_cero (bool) indica si se desea que exista el tiempo cero o no 
    def simulaPrimeraDinamica(self, tiempo_cero): 
        # Observación: el precio del producto va a ir disminuyendo a medida que hay más clientes que lo soliciten 

        # 1. Se simulan los clientes que están en un periodo determinado usando la app para comprar (CLIENTES)
        CLIENTES = simulaClientes(self.tasa_clientes_compran)
        # 2. Para cada producto,de los clientes simulados, se simula la cantidad de clientes que lo van a comprar y se muestrea esa cantidad de clientes de (CLIENTES)
        for producto, demanda in zip(self.productos["Nombre"], self.productos["demanda_clientes"]): 
            # Agregamos el producto a los descuentos aplicados
            self.DESCUENTOS_APLICADOS[producto] = []
            # Agregamos el producto a las cantidades solicitadas
            self.CANTIDADES_SOLICITADAS[producto] = 0 
            # Agregamos el producto a las cantidades no satisfechas
            self.CANTIDADES_NO_SATISFECHAS[producto] = 0
            # Vamos a muestrear sin reemplazo de CLIENTES 

            # Corrección de la variable demanda para que no sea mayor a la longitud de la población 
            if(demanda > len(CLIENTES)):
                demanda = len(CLIENTES)

            clientes_compran = random.sample(CLIENTES, demanda)
            # Extraemos la cantidad con la que se cuenta de ese producto 
            cantidad_del_producto = self.productos.loc[self.productos['Nombre'] == producto, 'cantidad'].values[0]
            
            # En caso que se dese correr una simulación con tiempo cero
            if(tiempo_cero):
                # 2.1. Para cada cliente se simula el método de descuento que se le va a aplicar
                for cliente in clientes_compran:
                    # Agregamos el producto al cliente 
                    # Simulamos de una uniforme discreta de 0 a cantidad_promedio[producto]
                    cantidad = np.random.randint(1, self.cantidad_promedio[producto])
                    if(self.CANTIDADES_SOLICITADAS[producto] + cantidad <= cantidad_del_producto): 
                        # Se agrega el producto a la canasta del cliente 
                        cliente.agregarProducto(producto, cantidad)
                        # Aplicamos el descuento 
                        descuento, tipo_descuento = aplicaDescuentoIndividual(cliente, self.forma_a, self.forma_b, producto)
                        # Vamos a guardar el descuento en un arreglo de descuentos para calcular posteriormente los ingresos por ventas (ya con el descuento aplicado)
                        # Este arreglo nos facilitará el cálculo de los descuentos por producto para no iterar por todos los clientes
                        self.DESCUENTOS_APLICADOS[producto].append(cantidad * (1 - descuento))
                        # Agregamos las cantidades solicitadas 
                        self.CANTIDADES_SOLICITADAS[producto] += cantidad
                        # Vamos a registrar el método por descuento 
                        if(tipo_descuento in self.METODOS_DESCUENTO):
                            self.METODOS_DESCUENTO[tipo_descuento] += 1
                        elif(tipo_descuento != None):
                            self.METODOS_DESCUENTO[tipo_descuento] = 1
                    else:
                        print(f'Se han agotado las existencias del producto {producto}')
                        self.CANTIDADES_NO_SATISFECHAS[producto] += cantidad

            # Ajustamos los productos solicitados al dataframe productos 
            self.productos.loc[self.productos["Nombre"] == producto, "productos_solicitados"] = self.CANTIDADES_SOLICITADAS[producto]

        self.ingresos, self.ingresos_x_producto = calculaIngresosConDescuento(self.DESCUENTOS_APLICADOS, self.productos)
        if(tiempo_cero):
            # Imprimimos los métodos de descuento que los clientes aplicaron durante la simulación 
            print(f'Métodos de descuento aplicados: {self.METODOS_DESCUENTO}')
            # Vamos a hacer una piechart utilizando plotly para desplegar los métodos de descuento
            fig = go.Figure(data=[go.Pie(labels=list(self.METODOS_DESCUENTO.keys()), values=list(self.METODOS_DESCUENTO.values()))], layout=go.Layout(title="Métodos de descuento aplicados"))
            # Cabiamos la tiografía de la gráfica
            fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
            fig.show()

            # 2.2 Se calculan los ingresos de ventas en total y por producto ya considerando los descuentos y cantidad de personas que solicitan cada producto 
            print(f'Ingresos totales: {self.ingresos} y por producto: {self.ingresos_x_producto}')

            # Vamos a hacer un piechart utilizando plotly para desplegar los ingresos por producto
            fig = go.Figure(data=[go.Pie(labels=list(self.ingresos_x_producto.keys()), values=list(self.ingresos_x_producto.values()))], layout=go.Layout(title="Ingresos por producto"))
            fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
            fig.show()

            # 3. Dependiendo del total de productos demandados, se va a escoger un camión que cuente con la capacidad suficiente para transportarlos (CAMIONES)
            espacio, peso_total = calculaEspacioCargamento(self.productos)
            print(f'Espacio total: {espacio} y peso total: {peso_total}')

            # 4. Gráfica de los productos no satisfechos (de barra y por producto) de self.CANTIDADES_NO_SATISFECHAS 
            fig = go.Figure(data=[go.Bar(x=list(self.CANTIDADES_NO_SATISFECHAS.keys()), y=list(self.CANTIDADES_NO_SATISFECHAS.values()))], layout=go.Layout(title="Cantidad de productos no satisfechos"))
            fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)
            fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
            fig.show()

            # Vamos a hacer una gráfica de barras para desplegar la cantidad de productos solicitados 
            fig = go.Figure(data=[go.Bar(x=list(self.CANTIDADES_SOLICITADAS.keys()), y=list(self.CANTIDADES_SOLICITADAS.values()))], layout=go.Layout(title="Cantidad de productos solicitados"))
            # Agregamos diferentes colores a la gráfica
            fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)
            fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
            fig.show()
            # Display de los productos
            display(self.productos)
    

    # Método que simula la dinámica de venta de productos en el tiempo 
    def simulaSegundaDinamica_tiempo(self): 
        # Estructuras de datos que contendrán el cambio en el tiempo de las variables de interés 
        self.cantidades_solicitadas_en_tiempo = {}
        for producto in self.productos["Nombre"]:
            # La cantidad_t0 es la cantidad de productos solicitados del dataframe de productos (antes de mandar el camión )
            cantidad_t0 = self.productos[self.productos["Nombre"] == producto]["productos_solicitados"].tolist()[0]
            self.cantidades_solicitadas_en_tiempo[producto] = [cantidad_t0]

        # Estructura que contiene los precios por producto en el tiempo
        precios_por_producto_en_tiempo = {}
        for producto in self.productos["Nombre"]:
            precio = self.productos[self.productos["Nombre"] == producto]["precio"].tolist()[0]
            precios_por_producto_en_tiempo[producto] = [precio]

        # Estructura que contiene los ingresos por producto en el tiempo 
        ingresos_por_producto_en_tiempo = {}
        for producto in self.productos["Nombre"]:
            ingreso = self.ingresos_x_producto[producto]
            ingresos_por_producto_en_tiempo[producto] = [ingreso]

        clientes_nuevos_tiempo = []
        ingresos_en_tiempo = [self.ingresos]
        cantidad_de_descuentos_aplicados_tiempo = []

        # 4. Se establece el punto inicial de la ruta y el punto final de la ruta (RUTAS) (Conexión con Google Maps para estimar el tiempo de llegada) (DONE)

        # Definimos un pool de clientes extemporáneos que tienen una probabilidad positiva de comprar productos 
        CLIENTES_EXTEMPORANEOS = simulaClientes(self.tasa_tota_nuevos_clientes)

        # 5. Se simula el tiempo que se tarda el camión en llegar a su destino 
        for i in range(self.tiempo): 
            j = 0 
            # Variable que va contando los clientes que en el tiempo t deciden comprar un producto
            cantidad_de_nuevos_clientes = 0 
            # Cantidad de descuentos asignados al tiempo i 
            descuentos_i = 0 

            for producto in self.productos["Nombre"]:
                # 5.1 Se simula la cantidad de nuevos clientes que van a comprar el producto en ese tiempo
                nuevos_clientes = simularDemanda(self.tasas_nuevos_clientes[producto])
                cantidad_de_nuevos_clientes += nuevos_clientes
                # Variable que regula la cantidad de nuevo producto solicitdado 
                nuevos_productos = 0 

                # 5.1 Por cada tiempo, se simula una cantidad de clientes que decidieron comprar el producto en ese tiempo  (se tiene que ver si hay productos disponibles)
                # 5.2 Por cada cliente se simula el método de descuento que se le va a aplicar
                # 5.3 Se actualizan los ingresos de ventas en total y por producto ya considerando los descuentos.

                # Corrección de la variable nuevos_clientes 
                if(nuevos_clientes > len(CLIENTES_EXTEMPORANEOS)):
                    nuevos_clientes = len(CLIENTES_EXTEMPORANEOS)

                clientes_compran = random.sample(CLIENTES_EXTEMPORANEOS, nuevos_clientes)
                # Extraemos la cantidad con la que se cuenta de ese producto 
                cantidad_del_producto = self.productos.loc[self.productos['Nombre'] == producto, 'cantidad'].values[0]
                # 2.1. Para cada cliente se simula el método de descuento que se le va a aplicar
                for cliente in clientes_compran:
                    # Agregamos el producto al cliente 
                    # Simulamos de una uniforme discreta de 0 a cantidad_promedio[producto]
                    cantidad = np.random.randint(0, self.cantidad_promedio[producto])
                    if(self.CANTIDADES_SOLICITADAS[producto] + cantidad <= cantidad_del_producto): 
                        cliente.agregarProducto(producto, cantidad)
                        # Aplicamos el descuento             
                        cliente.agregarProducto(producto, cantidad)

                        descuento, tipo_descuento = aplicaDescuentoIndividual(cliente, self.forma_a, self.forma_b, producto)
                        # Vamos a guardar el descuento en un arreglo de descuentos para calcular posteriormente los ingresos por ventas (ya con el descuento aplicado)
                        # Este arreglo nos facilitará el cálculo de los descuentos por producto para no iterar por todos los clientes
                        self.DESCUENTOS_APLICADOS[producto].append(cantidad * (1 - descuento))
                        # Agregamos las cantidades solicitadas 
                        self.CANTIDADES_SOLICITADAS[producto] += cantidad
                        nuevos_productos += cantidad
                        # Vamos a registrar el método por descuento 
                        if(tipo_descuento in self.METODOS_DESCUENTO):
                            self.METODOS_DESCUENTO[tipo_descuento] += 1
                        elif(tipo_descuento != None):
                            self.METODOS_DESCUENTO[tipo_descuento] = 1
                        
                        # Agregamos el descuento 
                        if(descuento != 0): 
                            descuentos_i += 1
                    else: 
                        # Si no hay suficiente producto, no se le vende al cliente 
                        print(f'Se han agotado las existencias del producto {producto}')
                        self.CANTIDADES_NO_SATISFECHAS[producto] += cantidad
                
                # Se actualiza el precio del producto y se disminuye en un factor porporcional a la variable de nuevos_productos (ACTUALIZAR)
                # Vamos a actualizarlo siempre y cuando el precio del producto sea mayor o igual al límite inferior
                if(self.productos.loc[self.productos["Nombre"] == producto, "precio"].tolist()[0] >= self.limites_inferiores[producto]):
                    # Actualización del precio 
                    self.productos.loc[self.productos["Nombre"] == producto, "precio"] = ajusta_precio(self.productos.loc[self.productos["Nombre"] == producto, "precio"], nuevos_clientes)

                # Ajustamos los productos solicitados al dataframe productos 
                self.productos.loc[self.productos["Nombre"] == producto, "productos_solicitados"] = self.CANTIDADES_SOLICITADAS[producto]

                # Actualizamos las series de tiempo 
                self.cantidades_solicitadas_en_tiempo[producto].append(nuevos_productos)
                precios_por_producto_en_tiempo[producto].append(self.productos.loc[self.productos["Nombre"] == producto, "precio"].tolist()[0])
                
            # Calculamos los ingresos después de la actualización 
            ingresos, ingresos_x_producto = calculaIngresosConDescuento(self.DESCUENTOS_APLICADOS, self.productos)

            # Vamos a actualizar ingreos_por_producto_en_tiempo
            for producto in self.productos["Nombre"]:
                ingresos_por_producto_en_tiempo[producto].append(ingresos_x_producto[producto])

            ingresos_en_tiempo.append(ingresos)
            cantidad_de_descuentos_aplicados_tiempo.append(descuentos_i)
            clientes_nuevos_tiempo.append(cantidad_de_nuevos_clientes)


        # Observaciones: 
        # Cuando hayan más clientes que soliciten un producto, el precio va a ir disminuyendo 

        display(self.productos)
        # Resultados (por camión)

        # Observaciones 
        # El procedimiento anterior se hará por camión. Por lo que se pueden cambiar las variables globales que hacen referencia a las tasas de demanda, descuentos ofrecidos y capacidad de los camiones.
        # Ya con estos datos, se puede aplicar una clusterización de usuarios para clasificarlos en grupos  que compran ciertos paquetes de productos. 

        # 1. Gráfica del precio por producto a lo largo del tiempo 
        fig = go.Figure()
        for producto in self.cantidades_solicitadas_en_tiempo:
            fig.add_trace(go.Scatter(x=np.arange(len(self.cantidades_solicitadas_en_tiempo[producto][1:])), y=self.cantidades_solicitadas_en_tiempo[producto][1:], name=producto))

        fig.update_layout(title="Cantidad de productos solicitados por producto a lo largo del tiempo", xaxis_title="Tiempo", yaxis_title="Cantidad de productos solicitados")
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()

        # 2. Gráfica de los ingresos por ventas a lo largo del tiempo 
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.arange(len(ingresos_en_tiempo[1:])), y=ingresos_en_tiempo[1:], name="Ingresos"))
        fig.update_layout(title="Ingresos por ventas a lo largo del tiempo", xaxis_title="Tiempo", yaxis_title="Ingresos")
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()

        # 3. Gráfica de los ingresos por ventas por producto a lo largo del tiempo
        fig = go.Figure()
        for producto in ingresos_por_producto_en_tiempo:
            fig.add_trace(go.Scatter(x=np.arange(len(ingresos_por_producto_en_tiempo[producto][1:])), y=ingresos_por_producto_en_tiempo[producto][1:], name=producto))
        fig.update_layout(title="Ingresos por ventas por producto a lo largo del tiempo", xaxis_title="Tiempo", yaxis_title="Ingresos")
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()

        # 4. Gráfica de los precios por producto a lo largo del tiempo
        fig = go.Figure()
        for producto in precios_por_producto_en_tiempo:
            fig.add_trace(go.Scatter(x=np.arange(len(precios_por_producto_en_tiempo[producto])), y=precios_por_producto_en_tiempo[producto], name=producto))
            # Vamos a agregar una línea horizontal punteada que sea el límite inferior del precio del producto y que sea del mismo color que la línea del producto
            fig.add_shape(type="line", x0=0, y0= self.limites_inferiores[producto], x1=len(precios_por_producto_en_tiempo[producto]), y1= self.limites_inferiores[producto], line=dict(color=fig.data[-1].line.color, width=1, dash="dash"))
        fig.update_layout(title="Precios por producto a lo largo del tiempo", xaxis_title="Tiempo", yaxis_title="Precios")
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()

        # 5. Gráfica de la cantidad de clientes que en el tiempo decide comprar un producto
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.arange(len(clientes_nuevos_tiempo)), y=clientes_nuevos_tiempo, name="Clientes"))
        fig.update_layout(title="Cantidad de clientes que en el tiempo decide comprar un producto", xaxis_title="Tiempo", yaxis_title="Cantidad de clientes")
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()

        # 6. Gráfica de pie para los métodos de descuento aplicados
        fig = go.Figure(data=[go.Pie(labels=list(self.METODOS_DESCUENTO.keys()), values=list(self.METODOS_DESCUENTO.values()))])
        fig.update_layout(title="Métodos de descuento aplicados")
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()

        # 7. Gráfica de la cantidad de descuentos aplicados a lo largo del tiempo
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.arange(len(cantidad_de_descuentos_aplicados_tiempo)), y=cantidad_de_descuentos_aplicados_tiempo, name="Descuentos"))
        fig.update_layout(title="Cantidad de descuentos aplicados a lo largo del tiempo", xaxis_title="Tiempo", yaxis_title="Cantidad de descuentos")
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()

        # 8. Gráfica de barras de los productos solicitados 
        fig = go.Figure(data=[go.Bar(x=list(self.CANTIDADES_SOLICITADAS.keys()), y=list(self.CANTIDADES_SOLICITADAS.values()))], layout=go.Layout(title="Cantidad de productos solicitados"))
        # Agregamos diferentes colores a la gráfica
        fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()

        # 9. Gráfica de los productos que fueron solicitados y que no pudieron ser colocados debido a que el producto se había agoatado
        fig = go.Figure(data=[go.Bar(x=list(self.CANTIDADES_NO_SATISFECHAS.keys()), y=list(self.CANTIDADES_NO_SATISFECHAS.values()))], layout=go.Layout(title="Cantidad de productos no satisfechos"))
        fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)
        fig.update_layout(font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
        fig.show()  

    # Main Simulation
    def run(self, tiempo_bool = True, tiempo_cero = True):
        # Ejecutamos la primera simulación en el tiempo 
        self.simulaPrimeraDinamica(tiempo_cero)
        if(tiempo_bool): 
            # Mostramos los resultados de la simulación en el tiempo 
            self.simulaSegundaDinamica_tiempo()
            