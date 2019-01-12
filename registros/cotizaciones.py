#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import fechas as Cal
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("abm_cotizaciones")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Cotizaciones")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_02").set_max_length(12)
        self.obj("txt_03").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de la Cotización")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("la Fecha de la Cotización"))
        self.obj("txt_02").set_tooltip_text("Ingrese el Monto de Compra de la Cotización")
        self.obj("txt_03").set_tooltip_text("Ingrese el Monto de Venta de la Cotización")
        self.obj("txt_01").grab_focus()

        self.idMoneda = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_moneda"), "monedas_s", "idMoneda")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond_id = str(seleccion.get_value(iterador, 0))
            self.cond_moneda = seleccion.get_value(iterador, 1)
            fecha = seleccion.get_value(iterador, 3)
            compra = str(seleccion.get_value(iterador, 4))
            venta = str(seleccion.get_value(iterador, 5))
            self.fecha = seleccion.get_value(iterador, 6)

            # Asignación de Monedas en Combo
            model, i = self.obj("cmb_moneda").get_model(), 0
            while model[i][0] != self.cond_moneda: i += 1
            self.obj("cmb_moneda").set_active(i)

            self.obj("txt_00").set_text(self.cond_id)
            self.obj("txt_01").set_text(fecha)
            self.obj("txt_02").set_text(compra)
            self.obj("txt_03").set_text(venta)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("cmb_moneda").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_02").get_text()
        v3 = self.obj("txt_03").get_text()

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + str(self.idMoneda) + ", '" + self.fecha + "', " + v2 + ", " + v3
        if not self.editando:
            Op.insertar(conexion, self.nav.tabla, sql)
        else:
            Op.modificar(conexion, self.nav.tabla, self.cond_id +
                ", " + str(self.cond_moneda) + ", " + sql)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_fecha_clicked(self, objeto):
        self.obj("txt_01").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.obj("txt_01").set_text(lista[0])
            self.fecha = lista[1]

    def on_btn_limpiar_fecha_clicked(self, objeto):
        self.obj("txt_01").set_text("")
        self.obj("txt_01").grab_focus()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0 \
        or self.idMoneda == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_02"), "Monto de Compra", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_03"), "Monto de Venta", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def on_cmb_moneda_changed(self, objeto):
        model = self.obj("cmb_moneda").get_model()
        active = self.obj("cmb_moneda").get_active()

        if active > -1:
            self.idMoneda = model[active][0]
            self.focus_out_event(self.obj("txt_00"), 0)
        else:
            self.obj("barraestado").push(0, "No existen registros de Monedas en el Sistema.")

    def on_txt_01_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_fecha_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def on_txt_01_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar una Fecha.")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond_id or str(self.idMoneda) != str(self.cond_moneda)) \
                and Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion,
                        self.nav.tabla + "_s", self.nav.campoid, valor +
                        " AND idMoneda = " + str(self.idMoneda), objeto,
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        "El Cód. de Cotización introducido ya ha sido registado para esta Moneda.")

            elif objeto == self.obj("txt_01"):
                if Op.compara_fechas(self.nav.datos_conexion, "'" + self.fecha + "'", ">", "NOW()"):
                    self.obj("btn_guardar").set_sensitive(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha NO puede estar en el Futuro.")
                else:
                    self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_02"):
                Op.comprobar_numero(float, self.obj("txt_02"), "Monto de Compra", self.obj("barraestado"))

            elif objeto == self.obj("txt_03"):
                Op.comprobar_numero(float, self.obj("txt_03"), "Monto de Venta", self.obj("barraestado"))


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Cód. Moneda", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Nombre", celda1, 2, True, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Fecha", celda0, 3, True, 200)
    col3.set_sort_column_id(6)  # Para ordenarse usa la fila 6
    col4 = Op.columnas("Compra", celda2, 4, True, 100, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Venta", celda2, 5, True, 100, 200)
    col5.set_sort_column_id(5)

    lista = [col0, col1, col2, col3, col4, col5]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(2)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 2)

    lista = ListStore(int, int, str, str, float, float, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar == "Fecha":
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", idMoneda, Moneda, " +
        "Fecha, Compra, Venta", self.tabla + "_s", opcion + " ORDER BY Fecha DESC")
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2],
            Cal.mysql_fecha(datos[i][3]), datos[i][4], datos[i][5],
            str(datos[i][3])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Código de Moneda", "idMoneda"
    elif idcolumna == 2:
        col, self.campo_buscar = "Nombre de Moneda", "Moneda"
    elif idcolumna == 6:
        col = self.campo_buscar = "Fecha"
        self.obj("txt_buscar").set_editable(False)
        self.obj("btn_buscar").set_visible(True)
    elif idcolumna == 4:
        col, self.campo_buscar = "Monto de Compra", "Compra"
    elif idcolumna == 5:
        col, self.campo_buscar = "Monto de Venta", "Venta"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = str(seleccion.get_value(iterador, 1))
    valor2 = seleccion.get_value(iterador, 2)
    valor3 = seleccion.get_value(iterador, 3)
    valor4 = str(seleccion.get_value(iterador, 3))
    valor5 = str(seleccion.get_value(iterador, 4))

    eleccion = Mens.pregunta_anular("Seleccionó:\n\nMoneda: " + valor2 +
        "\nFecha: " + valor3 + "\nCompra: " + valor4 + "\nVenta: " + valor5)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, valor0 + ", " + valor1)
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
    body_de = listado.tabla_celda_just_derecho()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Cód. Moneda", head), Par("Moneda", head),
        Par("Fecha", head), Par("Compra", head), Par("Venta", head)]]

    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_iz),
            Par(datos[i][2], body_ce), Par(str(datos[i][3]), body_de),
            Par(str(datos[i][4]), body_de)])

    listado.listado(self.titulo, lista, [70, 100, 100, 70, 70], A4)


def seleccion(self):
    pass
