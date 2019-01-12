#!/usr/bin/env python
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

        arch = Op.archivo("abm_timbrados")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Timbrados")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_02").set_max_length(10)

        self.obj("txt_00").set_tooltip_text("Ingrese el Nro. de Timbrado")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Establecimiento que afectará"))
        self.obj("txt_01_1").set_tooltip_text("Nombre del Establecimiento")
        self.obj("txt_01_2").set_tooltip_text("Dirección o Localización del Establecimiento")
        self.obj("txt_01_3").set_tooltip_text("Teléfono del Establecimiento")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Punto de Expedición que afectará"))
        self.obj("txt_02_1").set_tooltip_text("Nombre del Punto de Expedición")
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("la Fecha de Emisión del Timbrado"))
        self.obj("txt_04").set_tooltip_text(Mens.usar_boton("la Fecha de Vencimiento del Timbrado"))
        self.obj("txt_05").set_tooltip_text("Ingrese el Primer Número de Documento abarcado")
        self.obj("txt_06").set_tooltip_text("Ingrese el Último Número de Documento abarcado")
        self.obj("txt_00").grab_focus()

        mostrar_ventana = True
        self.txt_nro_est, self.txt_nom_est = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_dir_est, self.txt_tel_est = self.obj("txt_01_2"), self.obj("txt_01_3")
        self.txt_nro_cja, self.txt_nom_cja = self.obj("txt_02"), self.obj("txt_02_1")

        self.idTipoDoc = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo_doc"),
            "tipodocumentocomerciales", "idTipoDocumentoComercial")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            codcaja = str(seleccion.get_value(iterador, 7))
            caja = seleccion.get_value(iterador, 8)
            codestab = str(seleccion.get_value(iterador, 9))
            estab = seleccion.get_value(iterador, 10)
            ciudad = seleccion.get_value(iterador, 13)
            direccion = seleccion.get_value(iterador, 15)
            telefono = seleccion.get_value(iterador, 16)
            tipodoc = seleccion.get_value(iterador, 5)

            emision = seleccion.get_value(iterador, 1)
            vencimiento = seleccion.get_value(iterador, 2)
            inicio = seleccion.get_value(iterador, 3)
            ultimo = seleccion.get_value(iterador, 4)
            estado = seleccion.get_value(iterador, 20)

            direccion = "" if direccion is None else ", " + direccion
            telefono = "" if telefono is None else telefono

            if estado == "Vigente":
                self.fecha_emi = seleccion.get_value(iterador, 18)
                self.fecha_ven = seleccion.get_value(iterador, 19)

                # Asignación de Tipo de Documento en Combo
                model, i = self.obj("cmb_tipo_doc").get_model(), 0
                while model[i][0] != tipodoc: i += 1
                self.obj("cmb_tipo_doc").set_active(i)

                self.obj("txt_00").set_text(self.cond)
                self.obj("txt_01").set_text(codestab)
                self.obj("txt_01_1").set_text(estab)
                self.obj("txt_01_2").set_text(ciudad + direccion)
                self.obj("txt_01_3").set_text(telefono)
                self.obj("txt_02").set_text(codcaja)
                self.obj("txt_02_1").set_text(caja)
                self.obj("txt_03").set_text(emision)
                self.obj("txt_04").set_text(vencimiento)
                self.obj("txt_05").set_value(inicio)
                self.obj("txt_06").set_value(ultimo)
            else:
                Mens.no_puede_modificar_eliminar_anular(1, "Seleccionó:\n" +
                    "\nNro. Timbrado: " + self.cond + "\nCaja: " + codcaja + ", " + caja +
                    "\nEstablecimiento: " + codestab + ", " + estab + "\nDirección: " + ciudad + direccion +
                    "\n\nEste Nro. de Timbrado se encuentra actualmente " + estado + ".")
                self.obj("ventana").destroy()
                mostrar_ventana = False
        else:
            self.obj("txt_00").set_text("")
            self.obj("cmb_tipo_doc").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")

        if mostrar_ventana:
            self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()  # Establecimiento
        v3 = self.obj("txt_02").get_text()
        v4 = str(self.obj("txt_05").get_value_as_int())
        v5 = str(self.obj("txt_06").get_value_as_int())

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + v2 + ", " + v3 + ", " + str(self.idTipoDoc) + ", " + \
            "'" + self.fecha_emi + "', '" + self.fecha_ven + "', " + v4 + ", " + v5

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

    def on_btn_caja_clicked(self, objeto):
        establecimiento = None if len(self.obj("txt_01_2").get_text()) == 0 else self.obj("txt_01").get_text()

        from clases.llamadas import puntoexpediciones
        puntoexpediciones(self.nav.datos_conexion, self, establecimiento)

    def on_btn_fecha_emi_clicked(self, objeto):
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.fecha_emi = lista[1]
            self.obj("txt_03").set_text(lista[0])
            self.obj("txt_03").grab_focus()

    def on_btn_limpiar_fecha_emi_clicked(self, objeto):
        self.obj("txt_03").set_text("")
        self.obj("txt_03").grab_focus()

    def on_btn_fecha_ven_clicked(self, objeto):
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.fecha_ven = lista[1]
            self.obj("txt_04").set_text(lista[0])
            self.obj("txt_04").grab_focus()

    def on_btn_limpiar_fecha_ven_clicked(self, objeto):
        self.obj("txt_04").set_text("")
        self.obj("txt_04").grab_focus()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0 \
        or len(self.obj("txt_04").get_text()) == 0 or self.idTipoDoc == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Timbrado", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Nro. de Establecimiento", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Nro. de Punto de Expedición", self.obj("barraestado")):
                if self.obj("txt_05").get_value_as_int() > self.obj("txt_06").get_value_as_int():
                    estado = False
                    self.obj("barraestado").push(0, "El último número debe ser MAYOR al de inicio.")
                else:
                    estado = True
                    self.obj("barraestado").push(0, "")
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            self.idTipoDoc = model[active][0]
            self.verificacion(0)
        else:
            self.obj("barraestado").push(0, "No existen registros " +
            "de Tipo de Documentos Comerciales en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto == self.obj("txt_01"):
                    self.on_btn_establecimiento_clicked(0)
                elif objeto == self.obj("txt_02"):
                    self.on_btn_caja_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_fecha_emi_clicked(0)
                elif objeto == self.obj("txt_04"):
                    self.on_btn_fecha_ven_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto == self.obj("txt_01"):
            tipo = " Establecimiento"
        elif objeto == self.obj("txt_02"):
            tipo = " Punto de Expedición"
        elif objeto == self.obj("txt_03"):
            tipo = "a Fecha de Emisión"
        elif objeto == self.obj("txt_04"):
            tipo = "a Fecha de Vencimiento"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            self.limpiar_campos(objeto)
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original,
                # y si es un numero entero, comprueba si ya ha sido registado
                if (not self.editando or valor != self.cond) \
                and Op.comprobar_numero(int, self.obj("txt_00"), "Nro. de Timbrado", self.obj("barraestado")):
                    Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                        self.nav.campoid, valor, self.obj("txt_00"),
                        self.obj("btn_guardar"), self.obj("barraestado"),
                        "El Nro. de Timbrado introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
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

                        self.obj("txt_01_1").set_text(datos[0][0])
                        self.obj("txt_01_2").set_text(datos[0][1] + direccion)
                        self.obj("txt_01_3").set_text(telefono)

                        if datos[0][4] != 1:  # Si no está Activo
                            self.obj("btn_guardar").set_sensitive(False)
                            self.obj("txt_01").grab_focus()
                            self.obj("barraestado").push(0, "El Establecimiento seleccionado NO está Activo.")
                        else:
                            self.obj("barraestado").push(0, "")
                            self.focus_out_event(self.obj("txt_02"), 0)
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        self.obj("txt_01").grab_focus()
                        self.obj("barraestado").push(0, "El Nro. de Establecimiento NO es válido.")
                        self.limpiar_campos(objeto)

            elif objeto == self.obj("txt_02") and not len(self.obj("txt_01").get_text()) == 0:
                if Op.comprobar_numero(int, objeto, "Nro. de Punto de Expedición", self.obj("barraestado")):
                    conexion = Op.conectar(self.nav.datos_conexion)
                    cursor = Op.consultar(conexion, "Nombre, Activo",
                        "puntoexpediciones_s", " WHERE NroPuntoExpedicion = " + valor +
                        " AND NroEstablecimiento = " + self.obj("txt_01").get_text())
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        self.obj("txt_02_1").set_text(datos[0][0])

                        if datos[0][1] != 1:  # Si no está Activo
                            self.obj("btn_guardar").set_sensitive(False)
                            self.obj("txt_02").grab_focus()
                            self.obj("barraestado").push(0, "El Punto de Expedición seleccionado NO está Activo.")
                        else:
                            self.obj("barraestado").push(0, "")
                    else:
                        self.obj("btn_guardar").set_sensitive(False)
                        self.obj("txt_02").grab_focus()
                        self.obj("barraestado").push(0, "El Nro. de Punto de Expedición NO es válido.")
                        self.limpiar_campos(objeto)

            else:  # Fechas de Emisión y Vencimiento
                if len(self.obj("txt_03").get_text()) > 0 and len(self.obj("txt_04").get_text()) > 0:
                    if Op.compara_fechas(self.nav.datos_conexion,
                    "'" + self.fecha_emi + "'", ">", "'" + self.fecha_ven + "'"):
                        self.obj("btn_guardar").set_sensitive(False)
                        objeto.grab_focus()
                        self.obj("barraestado").push(0, "La Fecha de Emisión NO puede ser posterior a la Fecha de Vencimiento.")
                    else:
                        self.obj("barraestado").push(0, "")
                else:
                    self.obj("barraestado").push(0, "")

    def limpiar_campos(self, objeto):
        if objeto == self.obj("txt_01"):
            self.obj("txt_01_1").set_text("")
            self.obj("txt_01_2").set_text("")
        elif objeto == self.obj("txt_02"):
            self.obj("txt_02_1").set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Número", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Fecha de Emisión", celda1, 1, True, 200)
    col1.set_sort_column_id(18)  # Para ordenarse usa la fila 18
    col2 = Op.columnas("Fecha de Vencimiento", celda1, 2, True, 200)
    col2.set_sort_column_id(19)  # Para ordenarse usa la fila 19
    col3 = Op.columnas("Nro. Inicio", celda2, 3, True, 100, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Último Nro.", celda2, 4, True, 100, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Cód. Tipo Doc.", celda0, 5, True, 100, 200)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Documento Comercial", celda1, 6, True, 200)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Nro. Punto. Exp.", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Punto de Expedición", celda1, 8, True, 200)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Nro. Estab.", celda0, 9, True, 100, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Establecimiento", celda1, 10, True, 200)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("RUC Empresa", celda0, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Razón Social", celda1, 12, True, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Ciudad", celda1, 13, True, 150)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Barrio", celda1, 14, True, 150)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Dirección", celda1, 15, True, 250)
    col15.set_sort_column_id(15)
    col16 = Op.columnas("Teléfono", celda1, 16, True, 150)
    col16.set_sort_column_id(16)
    col17 = Op.columna_active("Anulado", 17)
    col17.set_sort_column_id(17)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8,
        col9, col10, col11, col12, col13, col14, col15, col16]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col17)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(0)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 0)

    lista = ListStore(int, str, str, int, int, int, str, int, str,
        int, str, str, str, str, str, str, str, bool, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar in ("FechaEmision", "FechaVencimiento"):
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " = '" + self.fecha + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        anulado = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Anulado = " + anulado

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", FechaEmision, " +
        "FechaVencimiento, NroInicio, NroFin, idTipoDocumentoComercial, " +
        "TipoDocumentoComercial, NroPuntoExpedicion, PuntoExpedicion, " +
        "NroEstablecimiento, Establecimiento, NroDocumento, RazonSocial, " +
        "Ciudad, Barrio, Direccion, NroTelefono, Anulado, Estado",
        self.tabla + "_s", opcion + " ORDER BY " + self.campoid + " DESC")
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], Cal.mysql_fecha(datos[i][1]),
            Cal.mysql_fecha(datos[i][2]), datos[i][3], datos[i][4],
            datos[i][5], datos[i][6], datos[i][7], datos[i][8],
            datos[i][9], datos[i][10], datos[i][11], datos[i][12],
            datos[i][13], datos[i][14], datos[i][15], datos[i][16],
            datos[i][17], str(datos[i][1]), str(datos[i][2]),
            datos[i][18]])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. de Timbrado", self.campoid
    elif idcolumna == 18:
        col, self.campo_buscar = "Fecha de Emisión", "FechaEmision"
        self.obj("txt_buscar").set_editable(False)
        self.obj("btn_buscar").set_visible(True)
    elif idcolumna == 19:
        col, self.campo_buscar = "Fecha de Vencimiento", "FechaVencimiento"
        self.obj("txt_buscar").set_editable(False)
        self.obj("btn_buscar").set_visible(True)
    elif idcolumna == 3:
        col, self.campo_buscar = "Nro. Inicio", "NroInicio"
    elif idcolumna == 4:
        col, self.campo_buscar = "Último Nro.", "NroFin"
    elif idcolumna == 5:
        col, self.campo_buscar = "Cód. Tipo Documento", "idTipoDocumentoComercial"
    elif idcolumna == 6:
        col, self.campo_buscar = "Documento Comercial", "TipoDocumentoComercial"
    elif idcolumna == 7:
        col, self.campo_buscar = "Nro. de Punto de Expedición", "NroPuntoExpedicion"
    elif idcolumna == 8:
        col, self.campo_buscar = "Nombre de Punto de Expedición", "PuntoExpedicion"
    elif idcolumna == 9:
        col, self.campo_buscar = "Nro. de Establecimiento", "NroEstablecimiento"
    elif idcolumna == 10:
        col, self.campo_buscar = "Nombre de Establecimiento", "Establecimiento"
    elif idcolumna == 11:
        col, self.campo_buscar = "RUC de la Empresa", "NroDocumento"
    elif idcolumna == 12:
        col, self.campo_buscar = "Razón Social", "RazonSocial"
    elif idcolumna == 13:
        col = self.campo_buscar = "Ciudad"
    elif idcolumna == 14:
        col = self.campo_buscar = "Barrio"
    elif idcolumna == 15:
        col, self.campo_buscar = "Dirección", "Direccion"
    elif idcolumna == 16:
        col, self.campo_buscar = "Teléfono", "Telefono"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = str(seleccion.get_value(iterador, 0))
    valor1 = str(seleccion.get_value(iterador, 7))
    valor2 = seleccion.get_value(iterador, 8)
    valor3 = str(seleccion.get_value(iterador, 9))
    valor4 = seleccion.get_value(iterador, 10)
    estado = seleccion.get_value(iterador, 20)

    valor5 = seleccion.get_value(iterador, 13)  # Ciudad
    valor6 = seleccion.get_value(iterador, 15)
    valor6 = "" if valor6 is None else ", " + valor6

    mensaje = "Seleccionó:\n\nNro. Timbrado: " + valor0 + "\nCaja: " + valor1 + ", " + valor2 + \
        "\nEstablecimiento: " + valor3 + ", " + valor4 + "\nDirección: " + valor5 + valor6

    if estado == "Vigente":
        eleccion = Mens.pregunta_anular(mensaje)
        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        if eleccion:
            conexion = Op.conectar(self.datos_conexion)
            Op.anular(conexion, self.tabla, valor0)
            conexion.commit()
            conexion.close()  # Finaliza la conexión
            cargar_grilla(self)
    else:
        Mens.no_puede_modificar_eliminar_anular(3, mensaje +
        "\n\nEste Nro. de Timbrado se encuentra actualmente " + estado + ".")


def listar_grilla(self):
    from clases import listado
    from reportlab.platypus import Paragraph as Par
    from reportlab.lib.pagesizes import A4, landscape

    datos = self.obj("grilla").get_model()
    cant = len(datos)

    head = listado.tabla_celda_titulo()
    body_ce = listado.tabla_celda_centrado()
    body_iz = listado.tabla_celda_just_izquierdo()
    body_de = listado.tabla_celda_just_derecho()

    lista = [[Par("Nro. Timbrado", head), Par("Nro. Establecimiento", head),
        Par("Nro. Caja", head), Par("Fecha de Emisión", head), Par("Fecha de Vencimiento", head),
        Par("Desde", head), Par("Hasta", head), Par("Estado", head)]]

    for i in range(0, cant):
        lista.append([Par(str(datos[i][0]), body_ce), Par(Op.cadenanumeros(datos[i][9], 3), body_ce),
            Par(Op.cadenanumeros(datos[i][7], 3), body_ce), Par(datos[i][1], body_iz),
            Par(datos[i][2], body_iz), Par(str(datos[i][3]), body_de),
            Par(str(datos[i][4]), body_de), Par(datos[i][20], body_ce)])

    listado.listado(self.titulo, lista, [100, 100, 100, 125, 125, 50, 50, 50], landscape(A4))


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        timb = str(seleccion.get_value(iterador, 0))
        caja = str(seleccion.get_value(iterador, 7))
        estab = str(seleccion.get_value(iterador, 9))

        self.origen.txt_nro_timb.set_text(timb)
        self.origen.txt_nro_cja.set_text(Op.cadenanumeros(caja, 3))
        self.origen.txt_nro_est.set_text(Op.cadenanumeros(estab, 3))

        self.on_btn_salir_clicked(0)
    except:
        pass
