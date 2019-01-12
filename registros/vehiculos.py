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

        arch = Op.archivo("abm_vehiculos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Vehículos")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(50)
        self.obj("txt_02").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Vehículo")
        self.obj("txt_01").set_tooltip_text("Ingrese el Número del Registro Único del Automotor (R.U.A.) del Vehículo")
        self.obj("txt_02").set_tooltip_text("Ingrese el Número de Placa del Vehículo")
        self.obj("txt_01").grab_focus()

        self.idMarcaVeh = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_marca"), "marcavehiculos", "idMarcaVehiculo")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            marca = seleccion.get_value(iterador, 1)
            rua = seleccion.get_value(iterador, 3)
            placa = seleccion.get_value(iterador, 4)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(rua)
            self.obj("txt_02").set_text(placa)

            # Asignación de Moneda en Combo
            model, i = self.obj("cmb_marca").get_model(), 0
            while model[i][0] != marca: i += 1
            self.obj("cmb_marca").set_active(i)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("cmb_marca").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + str(self.idMarcaVeh) + ", '" + v2 + "', '" + v3 + "'"
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
        or len(self.obj("txt_02").get_text()) == 0 or self.idMarcaVeh == -1:
            estado = False
        else:
            estado = Op.comprobar_numero(int, self.obj("txt_00"),
                "Código", self.obj("barraestado"))
        self.obj("btn_guardar").set_sensitive(estado)

    def on_cmb_marca_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idMarcaVeh = model[active][0]
            self.verificacion(0)
        else:
            self.obj("barraestado").push(0, "No existen registros de Marcas de Vehículos en el Sistema.")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
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
                # Comprueba si el Nro. R.U.A. ya ha sido registado
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "NroRUA", "'" + valor + "'" + busq, objeto, self.obj("btn_guardar"),
                    self.obj("barraestado"), "El Nro. R.U.A. introducido ya ha sido registado.")

            elif objeto == self.obj("txt_02"):
                busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                # Comprueba si el Nro. de Placa ya ha sido registado
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "NroPlaca", "'" + valor + "'" + busq, objeto, self.obj("btn_guardar"),
                    self.obj("barraestado"), "El Nro. de Placa introducido ya ha sido registado.")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Cód. Marca", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Marca", celda1, 2, True, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Nro. R.U.A.", celda0, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Nro. Placa", celda0, 4, True, 200)
    col4.set_sort_column_id(4)

    lista = [col0, col1, col2, col3, col4]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, int, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", idMarcaVehiculo, " +
        "MarcaVehiculo, NroRUA, NroPlaca", self.tabla + "_s",
        opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3], datos[i][4]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Código", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Código de Marca", "idMarcaVehiculo"
    elif idcolumna == 2:
        col, self.campo_buscar = "Marca", "MarcaVehiculo"
    elif idcolumna == 3:
        col, self.campo_buscar = "Nro. R.U.A.", "NroRUA"
    elif idcolumna == 4:
        col, self.campo_buscar = "Nro. Placa", "NroPlaca"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 2)
    valor2 = seleccion.get_value(iterador, 3)
    valor3 = seleccion.get_value(iterador, 4)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nCód.: " + valor0 + "\nMarca: " + valor1 +
        "\nNro. R.U.A.: " + valor2 + "\nNro. Placa: " + valor3)

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

    lista = [[Par("Código", head), Par("Marca", head),
        Par("Nro. R.U.A.", head), Par("Nro. Placa", head)]]

    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][2], body_iz),
            Par(datos[i][3], body_ce), Par(datos[i][4], body_ce)])

    listado.listado(self.titulo, lista, [100, 150, 150, 100], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 2)
        valor2 = seleccion.get_value(iterador, 3)
        valor3 = seleccion.get_value(iterador, 4)

        self.origen.txt_cod_veh.set_text(valor0)
        self.origen.txt_mar_veh.set_text(valor1)
        self.origen.txt_rua_veh.set_text(valor2)
        self.origen.txt_plk_veh.set_text(valor3)

        self.on_btn_salir_clicked(0)
    except:
        pass
