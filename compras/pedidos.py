#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("compra_pedidos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_default_size(750, 500)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.estadoedicion(True)
        self.estadoguardar(False)
        self.estadoitem(False)
        self.config_grilla_items()

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_1").set_max_length(40)
        self.obj("txt_02").set_max_length(14)
        self.obj("txt_03").set_max_length(100)

        self.obj("txt_00").set_tooltip_text("Ingrese el Número de " + self.nav.titulo)
        self.obj("txt_01").set_tooltip_text("Ingrese el Código del Ítem")
        self.obj("txt_01_1").set_tooltip_text("Ingrese el Código de Barras del Ítem")
        self.obj("txt_01_2").set_tooltip_text("Descripción del Ítem")
        self.obj("txt_01_3").set_tooltip_text("Presentación del Ítem")
        self.obj("txt_01_4").set_tooltip_text("Categoría del Ítem")
        self.obj("txt_02").set_tooltip_text("Ingrese la Cantidad de Ítems")
        self.obj("txt_03").set_tooltip_text("Ingrese una Observación sobre el Ítems")
        self.obj("txt_00").grab_focus()

        self.txt_cod_it, self.txt_bar_it, self.txt_nom_it = self.obj("txt_01"), \
            self.obj("txt_01_1"), self.obj("txt_01_2")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            fecha = seleccion.get_value(iterador, 1)[0:-9]  # Quita la Hora

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_fecha").set_text(fecha)
            self.encabezado_guardado = True
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("txt_fecha").set_text(Cal.mysql_fecha(date.today()))
            self.encabezado_guardado = False

        self.conexion = Op.conectar(self.nav.datos_conexion)
        self.cargar_grilla_items()

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.guardar_encabezado()
        self.conexion.commit()
        self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.conexion.rollback()
        self.conexion.close()  # Finaliza la conexión
        self.obj("ventana").destroy()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Pedido", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.encabezado_guardado = False
        self.estadoguardar(estado)

    def on_pedido_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            # Cuando crea nuevo registro o, al editar, valor es diferente del original,
            # y si es un numero entero, comprueba si ya ha sido registado
            if (not self.editando or valor != self.cond) and \
            Op.comprobar_numero(int, objeto, "Nro. de Pedido", self.obj("barraestado")):
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "NroPedidoCompra", valor, objeto, self.estadoguardar, self.obj("barraestado"),
                    "El Nro. de Pedido introducido ya ha sido registado.")

    def guardar_encabezado(self):
        # Si el encabezado no ha sido registrado
        if not self.encabezado_guardado:
            pedido = self.obj("txt_00").get_text()

            if not self.editando:
                Op.insertar(self.conexion, self.nav.tabla, pedido)
            else:
                Op.modificar(self.conexion, self.nav.tabla, self.cond + ", " + pedido)

            self.obj("txt_fecha").set_text(Cal.mysql_fecha(date.today()))
            self.encabezado_guardado = True
            self.editando = True
            self.cond = pedido

    def estadoedicion(self, estado):
        self.obj("txt_00").set_sensitive(estado)
        self.obj("btn_cancelar").set_sensitive(estado)

    def estadoguardar(self, estado):
        self.obj("btn_nuevo").set_sensitive(estado)
        self.obj("btn_modificar").set_sensitive(estado)
        self.obj("btn_eliminar").set_sensitive(estado)
        self.obj("grilla").set_sensitive(estado)

        # Obligatoriamente debe poseer un detalle para poder Guardar
        guardar = True if estado and len(self.obj("grilla").get_model()) > 0 else False
        self.obj("btn_guardar").set_sensitive(guardar)

##### Ítems ############################################################

    def config_grilla_items(self):
        celda0 = Op.celdas(0.5)
        celda1 = Op.celdas(0.0)
        celda2 = Op.celdas(1.0)

        col0 = Op.columnas("Cód. Ítem", celda0, 0, True, 70, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Código de Barras", celda0, 1, True, 150, 250)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Nombre", celda1, 2, True, 125, 250)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("Categoría", celda1, 3, True, 150, 250)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Presentacion", celda1, 4, True, 150, 250)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Cantidad", celda2, 5, True, 100, 150)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Observaciones", celda2, 6, True, 200)
        col6.set_sort_column_id(6)

        lista = [col0, col1, col2, col3, col4, col5, col6]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(1)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(int, str, str, str, str, float, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_items(self):
        cursor = Op.consultar(self.conexion, "idItem, CodigoBarras, Nombre, " +
            "Categoria, Presentacion, Cantidad, Observaciones", "pedidocompras_detalles_s",
            " WHERE NroPedidoCompra = " + self.obj("txt_00").get_text() + " ORDER BY idItem")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        lista = self.obj("grilla").get_model()
        lista.clear()

        for i in range(0, cant):
            lista.append([datos[i][0], datos[i][1], datos[i][2],
            datos[i][3], datos[i][4], datos[i][5], datos[i][6]])

        cant = str(cant) + " registro encontrado." if cant == 1 \
            else str(cant) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        self.editando_item = False
        self.funcion_item()

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            leerfila = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.editando_item = True
            self.funcion_item()

    def on_btn_eliminar_clicked(self, objeto):
        self.guardar_encabezado()

        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            item = str(seleccion.get_value(iterador, 0))
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            pedido = self.obj("txt_00").get_text()
            codbar = seleccion.get_value(iterador, 1)
            nomb = seleccion.get_value(iterador, 2)
            cant = str(seleccion.get_value(iterador, 5))

            codbar = "" if codbar is None else codbar

            eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
                "\nCódigo de Barras: " + codbar + "\nNombre: " + nomb +
                "\nCantidad: " + cant + " unidades")

            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                Op.eliminar(self.conexion, "pedidocompras_detalles", pedido + ", " + item)
                self.cargar_grilla_items()

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

##### Agregar-Modificar Ítems ##########################################

    def estadoitem(self, estado):
        self.obj("vbox1").set_visible(estado)
        self.obj("hbuttonbox_item").set_visible(estado)

    def funcion_item(self):
        self.guardar_encabezado()

        if self.editando_item:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            self.cond_item = str(seleccion.get_value(iterador, 0))
            bar = seleccion.get_value(iterador, 1)
            nomb = seleccion.get_value(iterador, 2)
            cat = seleccion.get_value(iterador, 3)
            pres = seleccion.get_value(iterador, 4)
            cant = str(seleccion.get_value(iterador, 5))
            obs = seleccion.get_value(iterador, 6)

            bar = "" if bar is None else bar
            obs = "" if obs is None else obs

            self.obj("txt_01").set_text(self.cond_item)
            self.obj("txt_01_1").set_text(bar)
            self.obj("txt_01_2").set_text(nomb)
            self.obj("txt_01_3").set_text(pres)
            self.obj("txt_01_4").set_text(cat)
            self.obj("txt_02").set_text(cant)
            self.obj("txt_03").set_text(obs)

        self.obj("btn_guardar_item").set_sensitive(False)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.estadoedicion(False)
        self.estadoguardar(False)
        self.estadoitem(True)

    def on_btn_guardar_item_clicked(self, objeto):
        self.guardar_encabezado()

        pedido = self.obj("txt_00").get_text()
        item = self.obj("txt_01").get_text()
        cant = self.obj("txt_02").get_text()

        obs = self.obj("txt_03").get_text()
        obs = "NULL" if len(obs) == 0 else "'" + obs + "'"

        sql = pedido + ", " + item + ", " + cant + ", " + obs
        if not self.editando_item:
            Op.insertar(self.conexion, "pedidocompras_detalles", sql)
        else:
            Op.modificar(self.conexion, "pedidocompras_detalles", self.cond_item + ", " + sql)

        self.cargar_grilla_items()
        self.on_btn_cancelar_item_clicked(0)

    def on_btn_cancelar_item_clicked(self, objeto):
        self.estadoedicion(True)
        self.estadoguardar(True)
        self.estadoitem(False)

        self.obj("txt_01").set_text("")
        self.obj("txt_01_1").set_text("")
        self.obj("txt_01_2").set_text("")
        self.obj("txt_01_3").set_text("")
        self.obj("txt_01_4").set_text("")
        self.obj("txt_02").set_text("")
        self.obj("txt_03").set_text("")

    def on_btn_item_clicked(self, objeto):
        from clases.llamadas import items
        items(self.nav.datos_conexion, self)

    def verificacion_item(self, objeto):
        if len(self.obj("txt_01").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Ítem", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_02"), "Cantidad de Ítems", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar_item").set_sensitive(estado)

    def on_item_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_item_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.on_item_focus_out_event(objeto, 0)

    def on_item_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un Ítem.")

    def on_item_focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_01"):
                self.obj("txt_01_1").set_text("")
        else:
            if objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Ítem", self.obj("barraestado")):
                    self.buscar_item(objeto, "idItem", valor, "Ítem")

            elif objeto == self.obj("txt_01_1"):
                self.buscar_item(objeto, "CodigoBarras", "'" + valor + "'", "Barras")

            elif objeto == self.obj("txt_02"):
                Op.comprobar_numero(float, objeto, "Cantidad de Ítems", self.obj("barraestado"))

    def buscar_item(self, objeto, campo, valor, nombre):
        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idItem, CodigoBarras, Nombre, " +
            "Presentacion, Categoria", "items_s", " WHERE " + campo + " = " + valor)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            self.obj("txt_01").set_text(str(datos[0][0]))
            codbar = "" if datos[0][1] is None else datos[0][1]
            self.obj("txt_01_1").set_text(codbar)
            self.obj("txt_01_2").set_text(datos[0][2])
            self.obj("txt_01_3").set_text(datos[0][3])
            self.obj("txt_01_4").set_text(datos[0][4])

            Op.comprobar_unique(self.nav.datos_conexion, "pedidocompras_detalles_s",
                "idItem", str(datos[0][0]) + " AND NroPedidoCompra = " + self.obj("txt_00").get_text(),
                self.obj("txt_01"), self.obj("btn_guardar_item"), self.obj("barraestado"),
                "El Ítem introducido ya ha sido registado en este Pedido.")
        else:
            objeto.grab_focus()
            self.obj("btn_guardar_item").set_sensitive(False)
            self.obj("barraestado").push(0, "El Código de " + nombre + " no es válido.")

            otro = self.obj("txt_01_1") if objeto == self.obj("txt_01") else self.obj("txt_01")
            otro.set_text("")

            self.obj("txt_01_2").set_text("")
            self.obj("txt_01_3").set_text("")
            self.obj("txt_01_4").set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Número", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Fecha", celda0, 1, True, 225, 300)
    col1.set_sort_column_id(5)  # Para ordenarse usa la fila 5
    col2 = Op.columnas("Cantidad de Ítems", celda2, 2, True, 100, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Alias de Usuario", celda1, 3, True, 150, 250)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Nombre de Usuario", celda1, 4, True, 225, 400)
    col4.set_sort_column_id(4)

    lista = [col0, col1, col2, col3, col4]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(0)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 0)

    lista = ListStore(int, str, int, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar == "FechaHora":
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", FechaHora, CantItems, " +
        "Alias, NombreApellido", self.tabla + "_s", opcion + " ORDER BY FechaHora DESC")
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], Cal.mysql_fecha_hora(datos[i][1]),
            datos[i][2], datos[i][3], datos[i][4], str(datos[i][1])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. de Pedido", self.campoid
    elif idcolumna == 5:
        col, self.campo_buscar = "Fecha", "FechaHora"
        self.obj("txt_buscar").set_editable(False)
        self.obj("btn_buscar").set_visible(True)
    elif idcolumna == 2:
        col, self.campo_buscar = "Cantidad de Ítems", "CantItems"
    elif idcolumna == 3:
        col, self.campo_buscar = "Alias de Usuario", "Alias"
    elif idcolumna == 4:
        col, self.campo_buscar = "Nombre de Usuario", "NombreApellido"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)[0:-9]
    valor2 = seleccion.get_value(iterador, 1)[-8:]
    valor3 = seleccion.get_value(iterador, 4)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
        "Nro de Pedido: " + valor0 + "\nFecha: " + valor1 +
        "\nHora: " + valor2 + "\nResponsable: " + valor3)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, valor0)
        conexion.commit()
        conexion.close()  # Finaliza la conexión
        cargar_grilla(self)


def listar_grilla(self):
    from clases import listado
    from reportlab.platypus import Paragraph as Par
    from reportlab.lib.pagesizes import A4

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Nro. Pedido", head), Par("Fecha de Modificación", head),
    Par("Alias de Usuario", head), Par("Nombre", head)]]
    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_ce),
        Par(datos[i][3], body_ce), Par(str(datos[i][4]), body_iz)])

    listado.listado(self.titulo, lista, [70, 125, 75, 150], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        pedido = str(seleccion.get_value(iterador, 0))

        self.origen.txt_nro_ped.set_text(pedido)
        self.origen.cargar_item_pedido()

        self.on_btn_salir_clicked(0)
    except:
        pass
