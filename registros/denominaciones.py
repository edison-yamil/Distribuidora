#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("abm_denominaciones")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Denominaciones")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(50)
        self.obj("txt_02").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de la Denominación")
        self.obj("txt_01").set_tooltip_text("Ingrese la Descripción de la Denominación")
        self.obj("txt_02").set_tooltip_text("Ingrese el Valor numérico de la Denominación")
        self.obj("txt_01").grab_focus()

        self.idMoneda = self.idTipoDen = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_moneda"), "monedas_s", "idMoneda")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_den"),
            "tipodenominaciones", "idTipoDenominacion")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            des = seleccion.get_value(iterador, 1)
            moneda = seleccion.get_value(iterador, 2)
            tipo = seleccion.get_value(iterador, 4)
            val = str(seleccion.get_value(iterador, 6))

            # Asignación de Moneda en Combo
            model, i = self.obj("cmb_moneda").get_model(), 0
            while model[i][0] != moneda: i += 1
            self.obj("cmb_moneda").set_active(i)

            # Asignación de Tipo de Denominación en Combo
            model, i = self.obj("cmb_tipo_den").get_model(), 0
            while model[i][0] != tipo: i += 1
            self.obj("cmb_tipo_den").set_active(i)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(des)
            self.obj("txt_02").set_text(val)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("cmb_moneda").set_active(0)
            self.obj("cmb_tipo_den").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + str(self.idMoneda) + ", " + str(self.idTipoDen) + ", '" + v2 + "', " + v3

        if not self.editando:
            Op.insertar(conexion, self.nav.tabla, sql)
        else:
            Op.modificar(conexion, self.nav.tabla, self.cond + ", " + sql)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or self.idTipoDen == -1 or self.idMoneda == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_02"), "Valor", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_moneda"):
                self.idMoneda = model[active][0]
            elif objeto == self.obj("cmb_tipo_den"):
                self.idTipoDen = model[active][0]
            self.verificacion(0)
        else:
            if objeto == self.obj("cmb_moneda"):
                tipo = "Monedas"
            elif objeto == self.obj("cmb_tipo_den"):
                tipo = "Tipos de Denominación"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, objeto, "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion,
                        self.nav.tabla + "_s", self.nav.campoid, valor, objeto,
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                # Si edita debe ser diferente a la denominacion y moneda originales
                busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                # Comprueba si la descripcion ya ha sido registada
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "Descripcion", "'" + valor + "'" + busq, objeto,
                    self.obj("btn_guardar"), self.obj("barraestado"),
                    "La Descripción introducida ya ha sido registada.")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Descripción", celda1, 1, True, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Cód. Moneda", celda0, 2, True, 100, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Moneda", celda1, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Cód. Tipo", celda0, 4, True, 100, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Tipo de Denominación", celda1, 5, True, 200)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Valor", celda2, 6, True, 100, 200)
    col6.set_sort_column_id(6)

    lista = [col0, col1, col2, col3, col4, col5, col6]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, str, int, str, int, str, float)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", Descripcion, " +
        "idMoneda, Moneda, idTipoDenominacion, TipoDenominacion, Valor",
        self.tabla + "_s", opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], datos[i][6]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Descripción", "Descripcion"
    elif idcolumna == 2:
        col, self.campo_buscar = "Cód. Moneda", "idMoneda"
    elif idcolumna == 3:
        col = self.campo_buscar = "Moneda"
    elif idcolumna == 4:
        col, self.campo_buscar = "Cód. Tipo", "idTipoDenominacion"
    elif idcolumna == 5:
        col, self.campo_buscar = "Tipo de Denominación", "TipoDenominacion"
    elif idcolumna == 6:
        col = self.campo_buscar = "Valor"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)
    valor2 = str(seleccion.get_value(iterador, 4))

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
        "Cód.: " + valor0 + "\nDescripción: " + valor1 + "\nValor: " + valor2)

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
    body_de = listado.tabla_celda_just_derecho()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Código", head), Par("Descripción", head),
        Par("Tipo de Denominación", head), Par("Valor", head)]]

    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_iz),
            Par(datos[i][3], body_iz), Par(str(datos[i][4]), body_de)])

    listado.listado(self.titulo, lista, [75, 150, 150, 100], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)

        self.origen.txt_cod_den.set_text(valor0)
        self.origen.txt_des_den.set_text(valor1)

        self.on_btn_salir_clicked(0)
    except:
        pass
