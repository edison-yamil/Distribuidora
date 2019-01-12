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

        arch = Op.archivo("abm_tarjetas")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Tarjetas")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(20)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_01_2").set_max_length(12)
        self.obj("txt_02").set_max_length(10)
        self.obj("txt_02_2").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Ingrese el Nro. de Tarjeta")
        self.obj("txt_01").set_tooltip_text(Mens.usar_boton("el Banco de la Tarjeta"))
        self.obj("txt_01_1").set_tooltip_text("Razón Social del Banco")
        self.obj("txt_01_2").set_tooltip_text("Ingrese el Nro. de Documento del Banco")
        self.obj("txt_01_3").set_tooltip_text("Dirección del Banco")
        self.obj("txt_01_4").set_tooltip_text("Teléfono del Banco")
        self.obj("txt_02").set_tooltip_text(Mens.usar_boton("el Titular de la Tarjeta"))
        self.obj("txt_02_1").set_tooltip_text("Razón Social del Titular")
        self.obj("txt_02_2").set_tooltip_text("Ingrese el Nro. de Documento del Titular")
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("la Fecha de Vencimiento de la Tarjeta"))
        self.obj("txt_00").grab_focus()

        self.idTipoDocBanco = self.idTipoDocTitular = self.idMarcaTarjeta = self.idTipoTarjeta = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_doc_banco"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_doc_titular"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_marca"), "marcatarjetas", "idMarcaTarjeta")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo"), "tipotarjetas", "idTipoTarjeta")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = seleccion.get_value(iterador, 0)
            banco = str(seleccion.get_value(iterador, 1))
            tip_banco = seleccion.get_value(iterador, 2)
            doc_banco = seleccion.get_value(iterador, 3)
            nom_banco = seleccion.get_value(iterador, 4)
            dir_banco = seleccion.get_value(iterador, 5)
            tel_banco = seleccion.get_value(iterador, 6)
            titular = str(seleccion.get_value(iterador, 7))
            tip_tit = seleccion.get_value(iterador, 8)
            doc_tit = seleccion.get_value(iterador, 9)
            nom_tit = seleccion.get_value(iterador, 10)
            marca = seleccion.get_value(iterador, 11)
            tipo = seleccion.get_value(iterador, 13)

            fecha = seleccion.get_value(iterador, 15)
            self.fecha_ven = seleccion.get_value(iterador, 16)

            dir_banco = "" if dir_banco is None else dir_banco
            tel_banco = "" if tel_banco is None else tel_banco

            # Asignación del Tipo de Documento (Banco) en Combo
            model, i = self.obj("cmb_doc_banco").get_model(), 0
            while model[i][0] != tip_banco: i += 1
            self.obj("cmb_doc_banco").set_active(i)

            # Asignación del Tipo de Documento (Titular) en Combo
            model, i = self.obj("cmb_doc_titular").get_model(), 0
            while model[i][0] != tip_tit: i += 1
            self.obj("cmb_doc_titular").set_active(i)

            self.obj("txt_00").set_text(self.cond)
            self.obj("txt_01").set_text(banco)
            self.obj("txt_01_1").set_text(nom_banco)
            self.obj("txt_01_2").set_text(doc_banco)
            self.obj("txt_01_3").set_text(dir_banco)
            self.obj("txt_01_4").set_text(tel_banco)
            self.obj("txt_02").set_text(titular)
            self.obj("txt_02_1").set_text(nom_tit)
            self.obj("txt_02_2").set_text(doc_tit)
            self.obj("txt_03").set_text(fecha)

            # Asignación de la Marca de Tarjeta
            model, i = self.obj("cmb_marca").get_model(), 0
            while model[i][0] != marca: i += 1
            self.obj("cmb_marca").set_active(i)

            # Asignación del Tipo de Tarjeta
            model, i = self.obj("cmb_tipo").get_model(), 0
            while model[i][0] != tipo: i += 1
            self.obj("cmb_tipo").set_active(i)
        else:
            self.obj("cmb_doc_banco").set_active(0)
            self.obj("cmb_doc_titular").set_active(0)
            self.obj("cmb_marca").set_active(0)
            self.obj("cmb_tipo").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v0 = self.obj("txt_00").get_text()
        v1 = self.obj("txt_01").get_text()  # Banco
        v2 = self.obj("txt_02").get_text()  # Titular

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = "'" + v0 + "', " + v1 + ", " + v2 + ", " + str(self.idMarcaTarjeta) + \
            ", " + str(self.idTipoTarjeta) + ", '" + self.fecha_ven + "'"

        if not self.editando:
            Op.insertar(conexion, self.nav.tabla, sql)
        else:
            Op.modificar(conexion, self.nav.tabla, "'" + self.cond + "', " + sql)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_banco_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_01"), self.obj("txt_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_01_2"), self.obj("cmb_doc_banco")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_01_3"), self.obj("txt_01_4")
        self.obj("txt_01").grab_focus()

        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "Empresa = 1")

    def on_btn_titular_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_02"), self.obj("txt_02_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_02_2"), self.obj("cmb_doc_titular")
        self.txt_dir_per = self.txt_tel_per = None
        self.obj("txt_02").grab_focus()

        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self)

    def on_btn_fecha_ven_clicked(self, objeto):
        self.obj("txt_03").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.fecha_ven = lista[1]
            self.obj("txt_03").set_text(lista[0])

    def on_btn_limpiar_fecha_ven_clicked(self, objeto):
        self.obj("txt_03").set_text("")
        self.obj("txt_03").grab_focus()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_01_2").get_text()) == 0 or len(self.obj("txt_02").get_text()) == 0 \
        or len(self.obj("txt_02_2").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0 \
        or self.idMarcaTarjeta == -1 or self.idTipoTarjeta == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_01"), "Cód. de Banco", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_02"), "Cód. de Titular", self.obj("barraestado")):
                estado = True
            else:
                estado = False
        self.obj("btn_guardar").set_sensitive(estado)

    def on_cmb_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_doc_banco"):
                self.idTipoDocBanco = model[active][0]
            elif objeto == self.obj("cmb_doc_titular"):
                self.idTipoDocTitular = model[active][0]
            elif objeto == self.obj("cmb_marca"):
                self.idMarcaTarjeta = model[active][0]
            elif objeto == self.obj("cmb_tipo"):
                self.idTipoTarjeta = model[active][0]
            self.verificacion(0)
        else:
            if objeto in (self.obj("cmb_doc_banco"), self.obj("cmb_doc_titular")):
                tipo = "Tipos de Documentos de Identidad"
            elif objeto == self.obj("cmb_marca"):
                tipo = "Marcas de Tarjetas"
            elif objeto == self.obj("cmb_tipo"):
                tipo = "Tipos de Tarjetas"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " de Tarjetas en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                    self.on_btn_banco_clicked(0)
                elif objeto in (self.obj("txt_02"), self.obj("txt_02_2")):
                    self.on_btn_titular_clicked(0)
                elif objeto == self.obj("txt_03"):
                    self.on_btn_fecha_ven_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
            tipo = "al Banco de la Tarjeta"
        elif objeto in (self.obj("txt_02"), self.obj("txt_02_2")):
            tipo = "al Titular de la Tarjeta"
        elif objeto == self.obj("txt_03"):
            tipo = "una Fecha de Vencimiento"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto in (self.obj("txt_01"), self.obj("txt_01_2")):
                self.obj("txt_01_1").set_text("")
                self.obj("txt_01_2").set_text("")
                self.obj("txt_01_3").set_text("")
                self.obj("txt_01_4").set_text("")
            elif objeto in (self.obj("txt_02"), self.obj("txt_02_2")):
                self.obj("txt_02_1").set_text("")
                self.obj("txt_02_2").set_text("")
        else:
            if objeto == self.obj("txt_00"):
                # Cuando crea nuevo registro o, al editar, valor es diferente del original
                busq = "" if not self.editando else " AND " + self.nav.campoid + " <> '" + self.cond + "'"

                Op.comprobar_unique(self.nav.datos_conexion, self.nav.tabla + "_s",
                    self.nav.campoid, "'" + valor + "'" + busq, objeto,
                    self.obj("btn_guardar"), self.obj("barraestado"),
                    "El Nro. de Tarjeta introducido ya ha sido registado.")

            elif objeto == self.obj("txt_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Banco", self.obj("barraestado")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Banco", objeto, self.obj("txt_01_1"),
                        self.obj("txt_01_2"), self.obj("cmb_doc_banco"),
                        self.obj("txt_01_3"), self.obj("txt_01_4"))

            elif objeto == self.obj("txt_01_2"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocBanco + "'",
                    "Nro. de Documento del Banco", self.obj("txt_01"),
                    self.obj("txt_01_1"), objeto, self.obj("cmb_doc_banco"),
                    self.obj("txt_01_3"), self.obj("txt_01_4"))

            elif objeto == self.obj("txt_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Titular", self.obj("barraestado")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Titular", objeto, self.obj("txt_02_1"),
                        self.obj("txt_02_2"), self.obj("cmb_doc_titular"))

            elif objeto == self.obj("txt_02_2"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocTitular + "'",
                    "Nro. de Documento del Titular", self.obj("txt_02"),
                    self.obj("txt_02_1"), objeto, self.obj("cmb_doc_titular"))

            elif objeto == self.obj("txt_03"):
                if Op.compara_fechas(self.nav.datos_conexion, "NOW()", ">=", "'" + self.fecha_ven + "'") == 1:
                    self.obj("btn_guardar").set_sensitive(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de Vencimiento debe estar en el FUTURO.")
                else:
                    self.obj("barraestado").push(0, "")

    def buscar_personas(self, objeto, campo, valor, nombre, cod_per, rzn_scl, nro_doc, tip_doc, dir_per=None, tel_per=None):
        if dir_per is None:
            otros_campos = opcion = ""
        else:
            otros_campos = ", DireccionPrincipal, TelefonoPrincipal"
            opcion = " AND Empresa = 1"

        conexion = Op.conectar(self.nav.datos_conexion)
        cursor = Op.consultar(conexion, "idPersona, RazonSocial, " +
            "NroDocumento, idTipoDocumento" + otros_campos, "personas_s",
            " WHERE " + campo + " = " + valor + opcion)
        datos = cursor.fetchall()
        cant = cursor.rowcount
        conexion.close()  # Finaliza la conexión

        if cant > 0:
            cod_per.set_text(str(datos[0][0]))
            rzn_scl.set_text(datos[0][1])
            nro_doc.set_text(datos[0][2])

            # Asignación de Tipo de Documento en Combo
            model, i = tip_doc.get_model(), 0
            while model[i][0] != datos[0][3]: i += 1
            tip_doc.set_active(i)

            if dir_per is not None:
                direccion = "" if datos[0][4] is None else datos[0][4]
                telefono = "" if datos[0][5] is None else datos[0][5]

                dir_per.set_text(direccion)
                tel_per.set_text(telefono)

            self.obj("barraestado").push(0, "")
            self.verificacion(0)

        else:
            self.obj("btn_guardar").set_sensitive(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = nro_doc if objeto == cod_per else cod_per
            otro.set_text("")
            rzn_scl.set_text("")

            if dir_per is not None:
                dir_per.set_text("")
                tel_per.set_text("")


def config_grilla(self):
    celda0 = Op.celdas(0.5)
    celda1 = Op.celdas(0.0)

    col0 = Op.columnas("Nro. Tarjeta", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Cód. Banco", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Tipo de Documento", celda1, 2, True, 150)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Nro. Documento", celda0, 3, True, 100, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Razón Social", celda1, 4, True, 200)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Dirección Principal", celda1, 5, True, 200, 500)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Teléfono Principal", celda0, 6, True, 100, 300)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Cód. Titular", celda0, 7, True, 100, 200)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Tipo de Documento", celda1, 8, True, 150)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Nro. Documento", celda0, 9, True, 100, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Razón Social", celda1, 10, True, 200)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Cód. Marca", celda0, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Marca de Tarjeta", celda1, 12, True, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Cód. Tipo", celda0, 13, True, 100, 200)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Tipo de Tarjeta", celda1, 14, True, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Fecha de Vencimiento", celda1, 15, True, 100, 200)
    col15.set_sort_column_id(16)  # Para ordenarse usa la fila 16

    lista = [col0, col1, col2, col3, col4, col5, col6,
        col7, col8, col9, col10, col11, col12, col13, col14, col15]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(0)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 0)

    lista = ListStore(str, int, str, str, str, str, str,
        int, str, str, str, int, str, int, str, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar == "FechaVencimiento":
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", idBanco, BancoTipoDocumento, " +
        "BancoNroDocumento, BancoRazonSocial, BancoDireccion, BancoTelefono, " +
        "idTitular, TitularTipoDocumento, TitularNroDocumento, TitularRazonSocial, " +
        "idMarcaTarjeta, MarcaTarjeta, idTipoTarjeta, TipoTarjeta, FechaVencimiento",
        self.tabla + "_s", opcion + " ORDER BY " + self.campoid)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
            datos[i][9], datos[i][10], datos[i][11], datos[i][12], datos[i][13],
            datos[i][14], Cal.mysql_fecha(datos[i][15]), str(datos[i][15])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Nro. Tarjeta", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Cód. Banco", "idBanco"
    elif idcolumna == 2:
        col, self.campo_buscar = "Tipo de Documento (Banco)", "BancoTipoDocumento"
    elif idcolumna == 3:
        col, self.campo_buscar = "Nro. Documento (Banco)", "BancoNroDocumento"
    elif idcolumna == 4:
        col, self.campo_buscar = "Razón Social (Banco)", "BancoRazonSocial"
    elif idcolumna == 5:
        col, self.campo_buscar = "Dirección (Banco)", "BancoDireccion"
    elif idcolumna == 6:
        col, self.campo_buscar = "Teléfono (Banco)", "BancoTelefono"
    elif idcolumna == 7:
        col, self.campo_buscar = "Cód. Titular", "idTitular"
    elif idcolumna == 8:
        col, self.campo_buscar = "Tipo de Documento (Titular)", "TitularTipoDocumento"
    elif idcolumna == 9:
        col, self.campo_buscar = "Nro. Documento (Titular)", "TitularNroDocumento"
    elif idcolumna == 10:
        col, self.campo_buscar = "Razón Social (Titular)", "TitularRazonSocial"
    elif idcolumna == 11:
        col, self.campo_buscar = "Cód. Marca", "idMarcaTarjeta"
    elif idcolumna == 12:
        col, self.campo_buscar = "Marca de Tarjeta", "MarcaTarjeta"
    elif idcolumna == 13:
        col, self.campo_buscar = "Cód. Tipo", "idTipoTarjeta"
    elif idcolumna == 14:
        col, self.campo_buscar = "Tipo de Tarjeta", "TipoTarjeta"
    elif idcolumna == 16:
        col, self.campo_buscar = "Fecha de Vencimiento", "FechaVencimiento"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    valor0 = seleccion.get_value(iterador, 0)
    valor1 = seleccion.get_value(iterador, 4)
    valor2 = seleccion.get_value(iterador, 10)
    valor3 = seleccion.get_value(iterador, 15)

    eleccion = Mens.pregunta_borrar("Seleccionó:\n" +
        "\nNro. Tarjeta: " + valor0 + "\nBanco: " + valor1 +
        "\nTitular: " + valor2 + "\nFecha de Vencimiento: " + valor3)

    self.obj("grilla").get_selection().unselect_all()
    self.obj("barraestado").push(0, "")

    if eleccion:
        conexion = Op.conectar(self.datos_conexion)
        Op.eliminar(conexion, self.tabla, "'" + valor0 + "'")
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

    lista = [[Par("Nro. Tarjeta", head), Par("Banco", head), Par("Titular", head),
        Par("Fecha de Vencimiento", head), Par("Tipo", head)]]
    for i in range(0, cant):
        lista.append([Par(datos[i][0], body_ce), Par(datos[i][4], body_iz),
            Par(datos[i][10], body_iz), Par(datos[i][15], body_ce),
            Par(datos[i][14], body_ce)])

    listado.listado(self.titulo, lista, [125, 170, 170, 150, 75], landscape(A4))


def seleccion(self):
    try:
        seleccion, iterador = self.obj("grilla").get_selection().get_selected()
        valor0 = seleccion.get_value(iterador, 0)

        valor1 = str(seleccion.get_value(iterador, 1))  # Banco
        valor2 = seleccion.get_value(iterador, 2)
        valor3 = seleccion.get_value(iterador, 3)
        valor4 = seleccion.get_value(iterador, 4)
        valor5 = seleccion.get_value(iterador, 5)
        valor6 = seleccion.get_value(iterador, 6)

        valor5 = "" if valor5 is None else valor5
        valor6 = "" if valor6 is None else valor5

        valor7 = str(seleccion.get_value(iterador, 7))  # Titular
        valor8 = seleccion.get_value(iterador, 8)
        valor9 = seleccion.get_value(iterador, 9)
        valor10 = seleccion.get_value(iterador, 10)

        self.origen.txt_nro_tj.set_text(valor0)

        # Asignación de Tipo de Documento (Banco) en Combo
        model, i = self.origen.cmb_doc_ban.get_model(), 0
        while model[i][0] != valor2: i += 1
        self.origen.cmb_doc_ban.set_active(i)

        self.origen.txt_cod_ban.set_text(valor1)
        self.origen.txt_scl_ban.set_text(valor4)
        self.origen.txt_doc_ban.set_text(valor3)
        self.origen.txt_dir_ban.set_text(valor5)
        self.origen.txt_tel_ban.set_text(valor6)

        # Asignación de Tipo de Documento (Titular) en Combo
        model, i = self.origen.cmb_doc_tit.get_model(), 0
        while model[i][0] != valor8: i += 1
        self.origen.cmb_doc_tit.set_active(i)

        self.origen.txt_cod_tit.set_text(valor7)
        self.origen.txt_scl_tit.set_text(valor10)
        self.origen.txt_doc_tit.set_text(valor9)

        self.on_btn_salir_clicked(0)
    except:
        pass
