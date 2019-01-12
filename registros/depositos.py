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

        arch = Op.archivo("abm_depositos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(50)
        self.obj("txt_02").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Depósito")
        self.obj("txt_01").set_tooltip_text("Ingrese la Descripción del Depósito")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Establecimiento en que se encuentra el Depósito"))
        self.obj("txt_02_1").set_tooltip_text("Nombre del Establecimiento")
        self.obj("txt_02_2").set_tooltip_text("Dirección del Establecimiento")
        self.obj("txt_02_3").set_tooltip_text("Teléfono del Establecimiento")
        self.obj("txt_01").grab_focus()

        self.txt_nro_est, self.txt_nom_est = self.obj("txt_02"), self.obj("txt_02_1")
        self.txt_dir_est, self.txt_tel_est = self.obj("txt_02_2"), self.obj("txt_02_3")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            nombre = seleccion.get_value(iterador, 1)
            codestab = str(seleccion.get_value(iterador, 2))
            estab = seleccion.get_value(iterador, 3)
            direccion = seleccion.get_value(iterador, 4)
            telefono = seleccion.get_value(iterador, 5)

            telefono = "" if telefono is None else telefono
            act = True if seleccion.get_value(iterador, 6) == 1 else False

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(nombre)
            self.obj("txt_02").set_text(codestab)
            self.obj("txt_02_1").set_text(estab)
            self.obj("txt_02_2").set_text(direccion)
            self.obj("txt_02_3").set_text(telefono)
            self.obj("rad_activo").set_active(act)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla, self.nav.campoid))

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()  # Establecimiento
        v4 = "1" if self.obj("rad_activo").get_active() else "0"

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + v3 + ", '" + v2 + "', " + v4
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

    def on_btn_establecimiento_clicked(self, objeto):
        from clases.llamadas import establecimientos
        establecimientos(self.nav.datos_conexion, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Nro. Establecimiento", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def on_txt_02_key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                self.on_btn_establecimiento_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def on_txt_02_focus_in_event(self, objeto, evento):
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un Establecimiento.")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_02"):
                self.obj("txt_02_1").set_text("")
                self.obj("txt_02_2").set_text("")
                self.obj("txt_02_3").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) and \
                Op.comprobar_numero(int, self.obj("txt_00"), "Código", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                        self.nav.campoid, valor, self.obj("txt_00"),
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        "El Código introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                busc = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond
                # Comprueba si el nombre o la descripcion ya ha sido registado/a
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "Descripcion", "'" + valor + "'" + busc, objeto, self.obj("btn_guardar"),
                    self.obj("barraestado"), "La Descripción introducida ya ha sido registada.")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Nro. Establecimiento", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "Nombre, Ciudad, " +
                        "Direccion, NroTelefono", "establecimientos_s",
                        " WHERE NroEstablecimiento = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        direccion = "" if datos[0][2] is None else ", " + datos[0][2]
                        telefono = "" if datos[0][3] is None else datos[0][3]

                        self.obj("txt_02_1").set_text(datos[0][0])
                        self.obj("txt_02_2").set_text(datos[0][1] + direccion)
                        self.obj("txt_02_3").set_text(telefono)
                        self.obj("barraestado").push(0, "")
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "El Nro. Establecimiento no es válido.")
                        self.obj("txt_02_1").set_text("")
                        self.obj("txt_02_2").set_text("")
                        self.obj("txt_02_3").set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Código", celda0, 0, True, 100, 150)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Descripción", celda1, 1, True, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Nro. Estab.", celda0, 2, True, 100, 150)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Establecimiento", celda1, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Dirección", celda1, 4, True, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Nro. Teléfono", celda1, 5, True, 200)
    col5.set_sort_column_id(5)
    col6 = Op.columna_active("Activo", 6)
    col6.set_sort_column_id(6)

    lista = [col0, col1, col2, col3, col4, col5]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col6)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, str, int, str, str, str, int)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", Descripcion, " +
        "NroEstablecimiento, Establecimiento, Direccion, NroTelefono, " +
        "Activo", self.tabla + "_s", opcion +
        " ORDER BY NroEstablecimiento, " + self.campoid)
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
        col, self.campo_buscar = "Nro. Establecimiento", "NroEstablecimiento"
    elif idcolumna == 3:
        col = self.campo_buscar = "Establecimiento"
    elif idcolumna == 4:
        col, self.campo_buscar = "Dirección", "Direccion"
    elif idcolumna == 5:
        col, self.campo_buscar = "Nro. Teléfono", "NroTelefono"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)
    valor2 = seleccion.get_value(iterador, 3)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\nCód.: " + valor0 +
        "\nDescripción: " + valor1 + "\nEstablecimiento: " + valor2)

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

    listafila = [Par("Código", head), Par(self.titulodos, head), Par(self.titulotres, head)]
    if self.tabla == "categorias":
        listafila.append(Par("Porc.", head))
        tamanos = [100, 200, 100, 50]
    else:
        tamanos = [100, 200, 100]

    lista = [listafila]
    for i in range(0, cant):
        listafila = [Par(str(datos[i][0]), body_ce),
        Par(datos[i][1], body_iz), Par(datos[i][2], body_iz)]

        if self.tabla == "categorias":
            listafila.append(Par(str(datos[i][3]), body_de))

        lista.append(listafila)

    listado.listado(self.titulo, lista, tamanos, A4)


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)

        self.origen.txt_cod_dep.set_text(valor0)
        self.origen.txt_des_dep.set_text(valor1)

        self.on_btn_salir_clicked(0)
    except:
        pass
