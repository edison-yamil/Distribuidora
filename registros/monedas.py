#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen):
        self.editando = edit
        self.nav = origen

        arch = Op.archivo("abm_monedas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Monedas")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(50)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_03").set_max_length(5)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de la Moneda")
        self.obj("txt_01").set_tooltip_text("Ingrese el Nombre de la Moneda")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el País de origen de la Moneda"))
        self.obj("txt_02_1").set_tooltip_text("Nombre del País")
        self.obj("txt_03").set_tooltip_text("Ingrese el Símbolo de la Moneda")
        self.obj("txt_01").grab_focus()

        self.txt_cod_pais, self.txt_des_pais = self.obj("txt_02"), self.obj("txt_02_1")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            nombre = seleccion.get_value(iterador, 1)
            codpais = str(seleccion.get_value(iterador, 2))
            pais = seleccion.get_value(iterador, 3)
            simbolo = seleccion.get_value(iterador, 4)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(nombre)
            self.obj("txt_02").set_text(codpais)
            self.obj("txt_02_1").set_text(pais)
            self.obj("txt_03").set_text(simbolo)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()  # País
        v4 = self.obj("txt_03").get_text()

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + v3 + ", '" + v2 + "', '" + v4 + "'"
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

    def on_btn_pais_clicked(self, objeto):
        from clases.llamadas import paises
        paises(self.nav.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de País", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def on_txt_02_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_pais_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def on_txt_02_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un País de origen.")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_02"):
                self.obj("txt_02_1").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion,
                        self.nav.tabla + "_s", self.nav.campoid, valor, objeto,
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                # Comprueba si el nombre ya ha sido registado
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "Nombre", "'" + valor + "'" + busq, objeto, self.obj("btn_guardar"),
                    self.obj("barraestado"), "El Nombre introducido ya ha sido registado.")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de País", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "Nombre",
                        "paises", " WHERE idPais = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_02_1").set_text(datos[0][0])
                        self.obj("barraestado").push(0, "")
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Cód. de País NO es válido.")
                        self.obj("txt_02_1").set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Nombre", celda1, 1, True, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Cód. País", celda0, 2, True, 100, 150)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("País", celda1, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Símbolo", celda0, 4, True, 100, 150)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Compra", celda2, 5, True, 100, 150)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Venta", celda2, 6, True, 100, 150)
    col6.set_sort_column_id(6)

    lista = [col0, col1, col2, col3, col4]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col5)
    self.obj("grilla").append_column(col6)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, str, int, str, str, float, float)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", Nombre, " +
        "idPais, Pais, Simbolo, Compra, Venta", self.tabla + "_s",
        opcion + " ORDER BY " + self.campoid)
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
        col = self.campo_buscar = "Nombre"
    elif idcolumna == 2:
        col, self.campo_buscar = "Cód. País", "idPais"
    elif idcolumna == 3:
        col, self.campo_buscar = "País", "Pais"
    elif idcolumna == 4:
        col, self.campo_buscar = "Símbolo", "Simbolo"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)
    valor2 = seleccion.get_value(iterador, 3)
    valor3 = seleccion.get_value(iterador, 4)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nCód.: " + valor0 + "\nNombre: " + valor1 +
        "\nPaís: " + valor2 + "\nSímbolo: " + valor3)

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

    lista = [[Par("Código", head), Par("Nombre", head),
        Par("País", head), Par("Símbolo", head)]]

    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_iz),
            Par(datos[i][3], body_iz), Par(datos[i][4], body_ce)])

    listado.listado(self.titulo, lista, [100, 150, 150, 100], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)
        valor2 = str(seleccion.get_value(iterador, 5))
        valor3 = str(seleccion.get_value(iterador, 6))

        self.origen.txt_cod_mon.set_text(valor0)
        self.origen.txt_des_mon.set_text(valor1)

        try:  # Cotización Compra
            self.origen.txt_cot_comp.set_text(valor2)
        except:
            pass

        try:  # Cotización Venta
            self.origen.txt_cot_vent.set_text(valor3)
        except:
            pass

        self.on_btn_salir_clicked(0)
    except:
        pass
