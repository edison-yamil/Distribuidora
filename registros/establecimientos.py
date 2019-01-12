#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op


class funcion_abm:

    def __init__(self, edit, origen, empresa=False):
        self.editando = edit
        self.nav = origen
        self.desde_empresa = empresa

        arch = Op.archivo("abm_establecimientos")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Establecimiento")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(50)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_04").set_max_length(50)

        self.obj("txt_00").set_tooltip_text("Ingrese el Nro. de Establecimiento")
        self.obj("txt_01").set_tooltip_text("Ingrese el Nombre del Establecimiento")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("la Empresa a la que pertenece"))
        self.obj("txt_02_1").set_tooltip_text("Nombre de la Empresa")
        self.obj("txt_03").set_tooltip_text("Dirección o Localización de la Empresa")
        self.obj("txt_04").set_tooltip_text("Número de Teléfono del Establecimiento")
        self.obj("txt_01").grab_focus()

        self.txt_cod_emp, self.txt_rzn_scl = self.obj("txt_02"), self.obj("txt_02_1")
        self.idDirec, self.txt_des_dir = -1, self.obj("txt_03")

        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            nombre = seleccion.get_value(iterador, 1)
            razonsocial = seleccion.get_value(iterador, 3)
            ciudad = seleccion.get_value(iterador, 4)
            direccion = seleccion.get_value(iterador, 6)
            telefono = seleccion.get_value(iterador, 7)

            activo = True if seleccion.get_value(iterador, 8) == 1 else False
            direccion = "" if direccion is None else ", " + direccion
            telefono = "" if telefono is None else telefono

            empresa = str(seleccion.get_value(iterador, 9))
            self.idDirec = seleccion.get_value(iterador, 10)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(nombre)
            self.obj("txt_02").set_text(empresa)
            self.obj("txt_02_1").set_text(razonsocial)
            self.obj("txt_03").set_text(ciudad + direccion)
            self.obj("txt_04").set_text(telefono)
            self.obj("rad_activo").set_active(activo)
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                "establecimientos_s", "NroEstablecimiento"))
            self.obj("rad_activo").set_active(True)

        if self.desde_empresa:
            self.obj("txt_02").set_text(self.nav.obj("txt_00").get_text())
            self.obj("hbox3").set_visible(False)  # No permite cambiar de Empresa
            self.conexion = self.nav.conexion  # Utiliza la conexión de Empresas

            cursor = self.conexion.cursor()
            cursor.execute("SAVEPOINT establecimiento")
            cursor.close()
        else:
            self.conexion = Op.conectar(self.nav.datos_conexion)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()

        v4 = self.obj("txt_04").get_text()
        v4 = "NULL" if len(v4) == 0 else v4
        v5 = "1" if self.obj("rad_activo").get_active() else "0"

        sql = v1 + ", " + v3 + ", " + str(self.idDirec) + ", '" + v2 + "', " + v4 + ", " + v5

        if not self.editando:
            Op.insertar(self.conexion, "establecimientos", sql)
        else:
            Op.modificar(self.conexion, "establecimientos", self.cond + ", " + sql)

        if not self.desde_empresa:
            self.conexion.commit()
            self.conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()

        if self.desde_empresa:
            self.nav.cargar_grilla_establecimiento()
        else:
            cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        if not self.desde_empresa:
            self.conexion.rollback()
            self.conexion.close()  # Finaliza la conexión
        else:
            cursor = self.conexion.cursor()
            cursor.execute("ROLLBACK TO SAVEPOINT establecimiento")
            cursor.close()

        self.obj("ventana").destroy()

    def on_btn_empresa_clicked(self, objeto):
        from clases.llamadas import empresas
        empresas(self.nav.datos_conexion, self)

    def on_btn_direccion_clicked(self, objeto):
        from registros.direcciones import direcciones
        editando = False if len(self.obj("txt_03").get_text()) == 0 else True
        direcciones(editando, True, self)

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Establecimiento", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de Empresa", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_02"):
                    self.on_btn_empresa_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_direccion_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_02"):
            tipo = "Empresa"
        elif objeto == self.obj("txt_03"):
            tipo = "Dirección"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar una " + tipo + ".")

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
                Op.comprobar_numero(int, objeto, "Nro. de Establecimiento", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, "establecimientos_s",
                        "NroEstablecimiento", valor, self.obj("txt_00"),
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        "El Nro. de Establecimiento introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                busc = "" if not self.editando else " AND NroEstablecimiento <> " + self.cond
                # Comprueba si el nombre ya ha sido registado/a
                Op.comprobar_unique(self.nav.datos_conexion, "establecimientos_s",
                    "Nombre", "'" + valor + "'" + busc, self.obj("txt_01"),
                    self.obj("btn_guardar"), self.obj("barraestado"),
                    "El Nombre introducido ya ha sido registado.")

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Empresa", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "RazonSocial",
                        "empresas_s", " WHERE idEmpresa = " + valor)
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_02_1").set_text(datos[0][0])
                        self.obj("barraestado").push(0, "")
                        self.verificacion(0)
                    else:
                        objeto.grab_focus()
                        self.obj("btn_guardar").set_sensitive(False)
                        self.obj("txt_02_1").set_text("")
                        self.obj("barraestado").push(0, "El Cód. de Empresa no es válido.")

            elif objeto == self.obj("txt_03"):
                self.obj("barraestado").push(0, "")


def config_grilla(self, desde_empresa=False):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Número", celda0, 0, True, 75, 100)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Nombre", celda1, 1, True, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("RUC Empresa", celda0, 2, True, 100, 125)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Razón Social", celda1, 3, True, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Ciudad", celda1, 4, True, 150)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Barrio", celda1, 5, True, 150)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Dirección", celda1, 6, True, 250)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Nro. Teléfono", celda1, 7, True, 150)
    col7.set_sort_column_id(7)
    col8 = Op.columna_active("Activo", 8)
    col8.set_sort_column_id(8)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col8)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)

    if not desde_empresa:
        columna_buscar(self, 1)

    lista = ListStore(int, str, str, str, str, str, str, str, bool, int, int)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
    " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        activo = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Activo = " + activo

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, "NroEstablecimiento, Nombre, " +
        "NroDocumento, RazonSocial, Ciudad, Barrio, Direccion, " +
        "NroTelefono, Activo, idEmpresa, idDireccion", self.tabla + "_s",
        opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
            datos[i][9], datos[i][10]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. Establecimiento", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Nombre de Establecimiento", "Nombre"
    elif idcolumna == 2:
        col, self.campo_buscar = "RUC Empresa", "NroDocumento"
    elif idcolumna == 3:
        col, self.campo_buscar = "Razón Social", "RazonSocial"
    elif idcolumna == 4:
        col = self.campo_buscar = "Ciudad"
    elif idcolumna == 5:
        col = self.campo_buscar = "Barrio"
    elif idcolumna == 6:
        col, self.campo_buscar = "Dirección", "Direccion"
    elif idcolumna == 7:
        col, self.campo_buscar = "Nro. Telefono", "NroTelefono"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = seleccion.get_value(iterador, 1)
    valor2 = seleccion.get_value(iterador, 3)

    valor3 = seleccion.get_value(iterador, 4)  # Ciudad
    valor4 = seleccion.get_value(iterador, 6)
    valor4 = "" if valor4 is None else ", " + valor4

    eleccion = Mens.pregunta_borrar("Seleccionó:\n\n" +
        "Nro. de Establecimiento: " + valor0 + "\nNombre: " + valor1 +
        "\nDirección: " + valor3 + valor4 + "\nEmpresa: " + valor2)

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
    from reportlab.lib.pagesizes import A4, landscape

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()

    lista = [[Par("Nro. Est.", head), Par("Nombre", head), Par("Ciudad", head),
        Par("Barrio", head), Par("Dirección", head), Par("Activo", head)]]

    for i in range(0, cant):
        estado = "Activo" if datos[i][8] == 1 else "Inactivo"

        lista.append([Par(str(datos[i][0]), body_ce), Par(datos[i][1], body_iz),
            Par(datos[i][4], body_iz), Par(datos[i][5], body_iz), Par(datos[i][6], body_iz),
            Par(estado, body_ce)])

    listado.listado(self.titulo, lista, [75, 150, 100, 100, 250, 50], landscape(A4))


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = seleccion.get_value(iterador, 1)
        valor2 = seleccion.get_value(iterador, 4)  # Ciudad
        valor3 = seleccion.get_value(iterador, 6)
        valor4 = seleccion.get_value(iterador, 7)

        valor3 = "" if valor3 is None else ", " + valor3
        valor4 = "" if valor4 is None else valor4

        self.origen.txt_nro_est.set_text(valor0)
        self.origen.txt_nom_est.set_text(valor1)
        self.origen.txt_dir_est.set_text(valor2 + valor3)
        self.origen.txt_tel_est.set_text(valor4)

        self.on_btn_salir_clicked(0)
    except:
        pass
