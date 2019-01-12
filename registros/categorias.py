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

        arch = Op.archivo("abm_categorias")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Categorías")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(50)
        self.obj("txt_02").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código de la Categoría")
        self.obj("txt_01").set_tooltip_text("Ingrese la Descripción de la Categoría")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Impuesto que grava la Categoría"))
        self.obj("txt_02_1").set_tooltip_text("Nombre del Impuesto que grava la Categoría")
        self.obj("txt_03").set_tooltip_text("Porcentaje que grava el Impuesto a la Categoría")
        self.obj("txt_01").grab_focus()

        self.txt_cod_imp, self.txt_des_imp, self.txt_por_imp = self.obj("txt_02"), \
            self.obj("txt_02_1"), self.obj("txt_03")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            descrip = seleccion.get_value(iterador, 1)
            codimp = str(seleccion.get_value(iterador, 2))
            imp = seleccion.get_value(iterador, 3)
            porc = str(seleccion.get_value(iterador, 4))

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(descrip)
            self.obj("txt_02").set_text(codimp)
            self.obj("txt_02_1").set_text(imp)
            self.obj("txt_03").set_text(porc)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()  # Impuesto

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + v3 + ", '" + v2 + "'"
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

    def on_btn_impuesto_clicked(self, objeto):
        from clases.llamadas import impuestos
        impuestos(self.nav.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de Impuesto", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def on_txt_02_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_impuesto_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def on_txt_02_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un Impuesto.")

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
                busc = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                # Comprueba si la descripcion ya ha sido registada
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "Descripcion", "'" + valor + "'" + busc, objeto, self.obj("btn_guardar"),
                    self.obj("barraestado"), "La Descripción introducida ya ha sido registada.")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Impuesto", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "Nombre, Porcentaje",
                        "impuestos", " WHERE idImpuesto = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_02_1").set_text(datos[0][0])
                        self.obj("txt_03").set_text(str(datos[0][1]))
                        self.obj("barraestado").push(0, "")
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Cód. de Impuesto NO es válido.")
                        self.obj("txt_02_1").set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Descripción", celda1, 1, True, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Cód. Impuesto", celda0, 2, True, 100, 150)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Impuesto", celda1, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Porcentaje", celda2, 4, True, 100, 150)
    col4.set_sort_column_id(4)

    lista = [col0, col1, col2, col3, col4]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, str, int, str, float)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", Descripcion, " +
        "idImpuesto, Impuesto, Porcentaje", self.tabla + "_s",
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
        col, self.campo_buscar = "Descripción", "Descripcion"
    elif idcolumna == 2:
        col, self.campo_buscar = "Cód. Impuesto", "idImpuesto"
    elif idcolumna == 3:
        col = self.campo_buscar = "Impuesto"
    elif idcolumna == 4:
        col = self.campo_buscar = "Porcentaje"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)
    valor2 = seleccion.get_value(iterador, 3)
    valor3 = str(seleccion.get_value(iterador, 4))

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nCód.: " + valor0 + "\nDescripción: " + valor1 +
        "\nImpuesto: " + valor2 + "\nPorcentaje: " + valor3)

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
        Par("Impuesto", head), Par("Porc.", head)]]

    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_iz),
            Par(datos[i][3], body_iz), Par(str(datos[i][4]), body_de)])

    listado.listado(self.titulo, lista, [100, 200, 100, 50], A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)
        valor2 = str(seleccion.get_value(iterador, 4))

        self.origen.txt_cod_cat.set_text(valor0)
        self.origen.txt_des_cat.set_text(valor1)

        try:
            self.origen.txt_por_imp.set_text(valor2)
        except:
            pass

        self.on_btn_salir_clicked(0)
    except:
        pass
