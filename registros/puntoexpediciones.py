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

        arch = Op.archivo("abm_puntoexpediciones")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de " + self.nav.titulo)
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(50)
        self.obj("txt_02").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Punto de Expedición")
        self.obj("txt_01").set_tooltip_text("Ingrese el Nombre del Punto de Expedición")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Establecimiento en que está localizado"))
        self.obj("txt_02_1").set_tooltip_text("Nombre del Establecimiento")
        self.obj("txt_02_2").set_tooltip_text("Dirección o Localización del Establecimiento")
        self.obj("txt_02_3").set_tooltip_text("Teléfono del Establecimiento")
        self.obj("txt_01").grab_focus()

        self.txt_nro_est, self.txt_nom_est = self.obj("txt_02"), self.obj("txt_02_1")
        self.txt_dir_est, self.txt_tel_est = self.obj("txt_02_2"), self.obj("txt_02_3")

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond_cja = str(seleccion.get_value(iterador, 0))
            nombre = seleccion.get_value(iterador, 1)
            self.cond_est = str(seleccion.get_value(iterador, 2))
            estab = seleccion.get_value(iterador, 3)
            ciudad = seleccion.get_value(iterador, 6)
            direccion = seleccion.get_value(iterador, 8)
            telefono = seleccion.get_value(iterador, 9)
            activo = True if seleccion.get_value(iterador, 10) == 1 else False

            direccion = "" if direccion is None else ", " + direccion
            telefono = "" if telefono is None else telefono

            self.obj("txt_00").set_text(self.cond_cja)
            self.obj("txt_01").set_text(nombre)
            self.obj("txt_02").set_text(self.cond_est)
            self.obj("txt_02_1").set_text(estab)
            self.obj("txt_02_2").set_text(ciudad + direccion)
            self.obj("txt_02_3").set_text(telefono)

            self.obj("rad_act").set_active(activo)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("rad_act").set_active(True)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()
        v4 = "1" if self.obj("rad_act").get_active() else "0"

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + v3 + ", '" + v2 + "', " + v4

        if not self.editando:
            Op.insertar(conexion, self.nav.tabla, sql)
        else:
            Op.modificar(conexion, self.nav.tabla, self.cond_cja +
                ", " + self.cond_est + ", " + sql)

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
            if Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Punto de Expedición", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Nro. de Establecimiento", self.obj("barraestado")):
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
            if objeto == self.obj("txt_00") and not len(self.obj("txt_02").get_text()) == 0:
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond_cja
                or self.obj("txt_02").get_text() != self.cond_est) \
                and Op.comprobar_numero(int, self.obj("txt_00"),
                "Nro. de Punto de Expedición", self.obj("barraestado")):
                    if Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    self.nav.campoid, valor + " AND NroEstablecimiento = " +
                    self.obj("txt_02").get_text(), objeto, self.obj("btn_guardar"),
                    self.obj("barraestado"), "El Nro. de Punto de Expedición " +
                    "introducido ya ha sido registado para este Establecimiento."):
                        self.focus_out_event(self.obj("txt_01"), 0)

            elif objeto == self.obj("txt_01") and not len(self.obj("txt_02").get_text()) == 0:
                busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond_cja
                # Comprueba si el nombre ya ha sido registado/a
                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    "Nombre", "'" + valor + "' AND NroEstablecimiento = " +
                    self.obj("txt_02").get_text() + busq, objeto,
                    self.obj("btn_guardar"), self.obj("barraestado"),
                    "El Nombre introducido ya ha sido registado para este Establecimiento.")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Nro. de Establecimiento", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "Nombre, Ciudad, Direccion, NroTelefono, Activo",
                        "establecimientos_s", " WHERE NroEstablecimiento = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        direccion = "" if datos[0][2] is None else ", " + datos[0][2]
                        telefono = "" if datos[0][3] is None else datos[0][3]

                        self.obj("txt_02_1").set_text(datos[0][0])
                        self.obj("txt_02_2").set_text(datos[0][1] + direccion)
                        self.obj("txt_02_3").set_text(telefono)

                        if datos[0][4] != 1:  # Si no está Activo
                            self.obj("btn_guardar").set_sensitive(False)
                            self.obj("txt_02").grab_focus()
                            self.obj("barraestado").push(0, "El Establecimiento seleccionado NO está Activo.")
                        else:
                            self.obj("barraestado").push(0, "")
                            self.focus_out_event(self.obj("txt_00"), 0)
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        self.obj("txt_02").grab_focus()
                        self.obj("barraestado").push(0, "El Nro. de Establecimiento NO es válido.")
                        self.obj("txt_02_1").set_text("")
                        self.obj("txt_02_2").set_text("")
                        self.obj("txt_02_3").set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Número", celda0, 0, True, 75, 100)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Nombre", celda1, 1, True, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Nro. Est.", celda0, 2, True, 75, 100)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Establecimiento", celda1, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("RUC Empresa", celda0, 4, True, 100, 125)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Razón Social", celda1, 5, True, 200)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Ciudad", celda1, 6, True, 150)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Barrio", celda1, 7, True, 150)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Dirección", celda1, 8, True, 250)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Teléfono", celda1, 9, True, 150)
    col9.set_sort_column_id(9)
    col10 = Op.columna_active("Activo", 10)
    col10.set_sort_column_id(10)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8, col9]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col10)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, str, int, str, str, str, str, str, str, str, bool)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        activo = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Activo = " + activo

    if len(self.condicion) > 0:
        self.condicion = " WHERE " + self.condicion if len(opcion) == 0 \
        else " AND " + self.condicion

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", Nombre, " +
        "NroEstablecimiento, Establecimiento, NroDocumento, RazonSocial, " +
        "Ciudad, Barrio, Direccion, NroTelefono, Activo", self.tabla + "_s",
        opcion + self.condicion + " ORDER BY NroEstablecimiento, " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], datos[i][6], datos[i][7],
            datos[i][8], datos[i][9], datos[i][10]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. de Punto de Expedición", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Nombre de Punto de Expedición", "Nombre"
    elif idcolumna == 2:
        col, self.campo_buscar = "Nro. Establecimiento", "NroEstablecimiento"
    elif idcolumna == 3:
        col, self.campo_buscar = "Nombre de Establecimiento", "Establecimiento"
    elif idcolumna == 4:
        col, self.campo_buscar = "RUC Empresa", "NroDocumento"
    elif idcolumna == 5:
        col, self.campo_buscar = "Razón Social", "RazonSocial"
    elif idcolumna == 6:
        col = self.campo_buscar = "Ciudad"
    elif idcolumna == 7:
        col = self.campo_buscar = "Barrio"
    elif idcolumna == 8:
        col, self.campo_buscar = "Dirección", "Direccion"
    elif idcolumna == 9:
        col, self.campo_buscar = "Teléfono", "NroTelefono"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)
    valor2 = str(seleccion.get_value(iterador, 2))
    valor3 = seleccion.get_value(iterador, 3)

    valor4 = seleccion.get_value(iterador, 6)  # Ciudad
    valor5 = seleccion.get_value(iterador, 8)
    valor5 = "" if valor5 is None else ", " + valor5

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nNro. de Punto de Expedición: " + valor0 + "\nNombre: " + valor1 +
        "\nEstablecimiento: " + valor3 + "\nDirección: " + valor4 + valor5)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, valor0 + ", " + valor2)
        conexion.commit()
        conexion.close()  # Finaliza la conexión
        cargar_grilla(self)


def listar_grilla(self):
    from clases import listado
    from reportlab.platypus import Paragraph as Par
    from reportlab.lib.pagesizes import A4, landscape

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Nro. Caja", head), Par("Nombre", head), Par("Nro. Est.", head),
        Par("Establecimiento", head), Par("Dirección", head), Par("Activo", head)]]

    for i in range(0, cant):
        estado = "Activo" if datos[i][10] == 1 else "Inactivo"

        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_iz),
        Par(str(datos[i][2]), body_ce), Par(datos[i][3], body_iz), Par(datos[i][8], body_iz),
        Par(estado, body_ce)])

    listado.listado(self.titulo, lista, [75, 150, 75, 125, 225, 50], landscape(A4))


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)
        valor2 = str(seleccion.get_value(iterador, 2))
        valor3 = seleccion.get_value(iterador, 3)
        valor4 = seleccion.get_value(iterador, 6)  # Ciudad
        valor5 = seleccion.get_value(iterador, 8)
        valor6 = seleccion.get_value(iterador, 9)

        valor5 = "" if valor5 is None else ", " + valor5
        valor6 = "" if valor6 is None else valor6

        self.origen.txt_nro_cja.set_text(valor0)
        self.origen.txt_nom_cja.set_text(valor1)
        self.origen.txt_nro_est.set_text(valor2)
        self.origen.txt_nom_est.set_text(valor3)
        self.origen.txt_dir_est.set_text(valor4 + valor5)
        self.origen.txt_tel_est.set_text(valor6)

        self.on_btn_salir_clicked(0)
    except:
        pass
