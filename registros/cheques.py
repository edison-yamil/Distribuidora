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

        arch = Op.archivo("abm_cheques")
        self.obj = arch.get_object

        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        edit = "Creando" if not self.editando else "Editando"
        self.obj("ventana").set_title(edit + " Registro de Cheques de Terceros")
        Mens.boton_guardar_cancelar(self.obj("btn_guardar"), self.obj("btn_cancelar"))

        self.obj("txt_00").set_max_length(10)
        self.obj("txt_01").set_max_length(10)
        self.obj("txt_02").set_max_length(20)
        self.obj("txt_03").set_max_length(10)
        self.obj("txt_03_2").set_max_length(12)
        self.obj("txt_04").set_max_length(10)
        self.obj("txt_04_2").set_max_length(12)
        self.obj("txt_07").set_max_length(12)

        self.obj("txt_00").set_tooltip_text("Ingrese el Código del Cheque")
        self.obj("txt_01").set_tooltip_text("Ingrese el Nro. de Cheque")
        self.obj("txt_02").set_tooltip_text("Ingrese el Nro. de Cuenta")
        self.obj("txt_03").set_tooltip_text(Mens.usar_boton("el Banco del Cheque"))
        self.obj("txt_03_1").set_tooltip_text("Razón Social del Banco")
        self.obj("txt_03_2").set_tooltip_text("Ingrese el Nro. de Documento del Banco")
        self.obj("txt_03_3").set_tooltip_text("Dirección del Banco")
        self.obj("txt_03_4").set_tooltip_text("Teléfono del Banco")
        self.obj("txt_04").set_tooltip_text(Mens.usar_boton("el Titular del Cheque"))
        self.obj("txt_04_1").set_tooltip_text("Razón Social del Titular")
        self.obj("txt_04_2").set_tooltip_text("Ingrese el Nro. de Documento del Titular")
        self.obj("txt_05").set_tooltip_text(Mens.usar_boton("la Fecha de Emisión del Cheque"))
        self.obj("txt_06").set_tooltip_text(Mens.usar_boton("la Fecha de Cobro del Cheque"))
        self.obj("txt_07").set_tooltip_text("Ingrese el Monto del Cheque")
        self.obj("txt_01").grab_focus()

        mostrar_ventana = True
        self.idTipoDocBanco = self.idTipoDocTitular = self.idTipoCheque = -1
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_doc_banco"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_doc_titular"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.nav.datos_conexion, self.obj("cmb_tipo"), "tipocheques", "idTipoCheque")
        arch.connect_signals(self)

        if self.editando:
            seleccion, iterador = self.nav.obj("grilla").get_selection().get_selected()
            self.cond = str(seleccion.get_value(iterador, 0))
            cheque = str(seleccion.get_value(iterador, 1))
            cuenta = seleccion.get_value(iterador, 2)
            banco = str(seleccion.get_value(iterador, 3))
            tip_banco = seleccion.get_value(iterador, 4)
            doc_banco = seleccion.get_value(iterador, 5)
            nom_banco = seleccion.get_value(iterador, 6)
            dir_banco = seleccion.get_value(iterador, 7)
            tel_banco = seleccion.get_value(iterador, 8)
            titular = str(seleccion.get_value(iterador, 9))
            tip_tit = seleccion.get_value(iterador, 10)
            doc_tit = seleccion.get_value(iterador, 11)
            nom_tit = seleccion.get_value(iterador, 12)
            tipo = seleccion.get_value(iterador, 13)
            emision = seleccion.get_value(iterador, 15)
            cobro = seleccion.get_value(iterador, 16)
            monto = str(seleccion.get_value(iterador, 17))
            anulado = seleccion.get_value(iterador, 18)

            if anulado != 1:
                self.fecha_emision = seleccion.get_value(iterador, 19)
                self.fecha_cobro = seleccion.get_value(iterador, 20)

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

                # Asignación del Tipo de Cheque en Combo
                model, i = self.obj("cmb_tipo").get_model(), 0
                while model[i][0] != tipo: i += 1
                self.obj("cmb_tipo").set_active(i)

                self.obj("txt_00").set_text(self.cond)
                self.obj("txt_01").set_text(cheque)
                self.obj("txt_02").set_text(cuenta)
                self.obj("txt_03").set_text(banco)
                self.obj("txt_03_1").set_text(nom_banco)
                self.obj("txt_03_2").set_text(doc_banco)
                self.obj("txt_03_3").set_text(dir_banco)
                self.obj("txt_03_4").set_text(tel_banco)
                self.obj("txt_04").set_text(titular)
                self.obj("txt_04_1").set_text(nom_tit)
                self.obj("txt_04_2").set_text(doc_tit)
                self.obj("txt_05").set_text(emision)
                self.obj("txt_06").set_text(cobro)
                self.obj("txt_07").set_text(monto)
            else:
                Mens.no_puede_modificar_eliminar_anular(1, "Seleccionó:\n" +
                    "\nNro. Cheque: " + cheque + "\nNro. Cuenta: " + cuenta +
                    "\nBanco: " + nom_banco + "\nTitular: " + nom_tit +
                    "\nFecha de Emisión: " + emision + "\nFecha de Cobro: " + cobro +
                    "\n\nEste Cheque se encuentra actualmente ANULADO.")
                self.obj("ventana").destroy()
                mostrar_ventana = False
        else:
            self.obj("txt_00").set_text(Op.nuevoid(self.nav.datos_conexion,
                self.nav.tabla + "_s", self.nav.campoid))
            self.obj("cmb_doc_banco").set_active(0)
            self.obj("cmb_doc_titular").set_active(0)
            self.obj("cmb_tipo").set_active(0)

        self.nav.obj("grilla").get_selection().unselect_all()
        self.nav.obj("barraestado").push(0, "")

        if mostrar_ventana:
            self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        v1 = self.obj("txt_00").get_text()
        v2 = self.obj("txt_01").get_text()
        v3 = self.obj("txt_02").get_text()
        v4 = self.obj("txt_03").get_text()  # Banco
        v5 = self.obj("txt_04").get_text()  # Titular
        v6 = self.obj("txt_07").get_text()

        # Establece la conexión con la Base de Datos
        conexion = Op.conectar(self.nav.datos_conexion)

        sql = v1 + ", " + v4 + ", " + v5 + ", " + str(self.idTipoCheque) + \
            ", " + v2 + ", '" + v3 + "', '" + self.fecha_emision + "', " + \
            "'" + self.fecha_cobro + "', " + v6

        if not self.editando:
            Op.insertar(conexion, self.nav.tabla, sql)
        else:
            Op.modificar(conexion, self.nav.tabla, str(self.cond) + ", " + sql)

        conexion.commit()
        conexion.close()  # Finaliza la conexión

        self.obj("ventana").destroy()
        cargar_grilla(self.nav)

    def on_btn_cancelar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_banco_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_03"), self.obj("txt_03_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_03_2"), self.obj("cmb_doc_banco")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_03_3"), self.obj("txt_03_4")
        self.obj("txt_03").grab_focus()

        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self, "Empresa = 1")

    def on_btn_titular_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_04"), self.obj("txt_04_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_04_2"), self.obj("cmb_doc_titular")
        self.txt_dir_per = self.txt_tel_per = None
        self.obj("txt_04").grab_focus()

        from clases.llamadas import personas
        personas(self.nav.datos_conexion, self)

    def on_btn_fecha_emision_clicked(self, objeto):
        self.obj("txt_05").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.fecha_emision = lista[1]
            self.obj("txt_05").set_text(lista[0])

    def on_btn_limpiar_fecha_emision_clicked(self, objeto):
        self.obj("txt_05").set_text("")
        self.obj("txt_05").grab_focus()

    def on_btn_fecha_cobro_clicked(self, objeto):
        self.obj("txt_06").grab_focus()
        self.obj("barraestado").push(0, "")
        lista = Cal.calendario()

        if lista is not False:
            self.fecha_cobro = lista[1]
            self.obj("txt_06").set_text(lista[0])

    def on_btn_limpiar_fecha_cobro_clicked(self, objeto):
        self.obj("txt_06").set_text("")
        self.obj("txt_06").grab_focus()

    def verificacion(self, objeto):
        if len(self.obj("txt_00").get_text()) == 0 or len(self.obj("txt_01").get_text()) == 0 \
        or len(self.obj("txt_02").get_text()) == 0 or len(self.obj("txt_03").get_text()) == 0 \
        or len(self.obj("txt_03_2").get_text()) == 0 or len(self.obj("txt_04").get_text()) == 0 \
        or len(self.obj("txt_04_2").get_text()) == 0 or len(self.obj("txt_05").get_text()) == 0 \
        or len(self.obj("txt_06").get_text()) == 0 or len(self.obj("txt_07").get_text()) == 0 \
        or self.idTipoCheque == -1:
            estado = False
        else:
            if Op.comprobar_numero(int, self.obj("txt_00"), "Cód. de Cheque", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_01"), "Nro. de Cheque", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_03"), "Cód. de Banco", self.obj("barraestado")) \
            and Op.comprobar_numero(int, self.obj("txt_04"), "Cód. de Titular", self.obj("barraestado")) \
            and Op.comprobar_numero(float, self.obj("txt_07"), "Monto del Cheque", self.obj("barraestado")):
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
            elif objeto == self.obj("cmb_tipo"):
                self.idTipoCheque = model[active][0]
            self.verificacion(0)
        else:
            if objeto in (self.obj("cmb_doc_banco"), self.obj("cmb_doc_titular")):
                tipo = "Tipos de Documentos de Identidad"
            elif objeto == self.obj("cmb_tipo"):
                tipo = "Tipos de Cheques"
            self.obj("barraestado").push(0, "No existen registros de " + tipo + " en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_03"), self.obj("txt_03_2")):
                    self.on_btn_banco_clicked(0)
                elif objeto in (self.obj("txt_04"), self.obj("txt_04_2")):
                    self.on_btn_titular_clicked(0)
                elif objeto == self.obj("txt_05"):
                    self.on_btn_fecha_emision_clicked(0)
                elif objeto == self.obj("txt_06"):
                    self.on_btn_fecha_cobro_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_03"), self.obj("txt_03_2")):
            tipo = "al Banco del Cheque"
        elif objeto in (self.obj("txt_04"), self.obj("txt_04_2")):
            tipo = "al Titular del Cheque"
        elif objeto == self.obj("txt_05"):
            tipo = "una Fecha de Emisión"
        elif objeto == self.obj("txt_06"):
            tipo = "una Fecha de Cobro"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar " + tipo + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")
            if objeto == self.obj("txt_03"):
                self.obj("txt_03_1").set_text("")
                self.obj("txt_03_2").set_text("")
                self.obj("txt_03_3").set_text("")
                self.obj("txt_03_4").set_text("")
            elif objeto == self.obj("txt_04"):
                self.obj("txt_04_1").set_text("")
                self.obj("txt_04_2").set_text("")
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
                if Op.comprobar_numero(int, objeto, "Nro. de Cheque", self.obj("barraestado")):
                    self.comprobar_cheque(objeto)

            elif objeto == self.obj("txt_02"):
                self.comprobar_cheque(objeto)

            elif objeto == self.obj("txt_03"):
                if Op.comprobar_numero(int, objeto, "Cód. de Banco", self.obj("barraestado")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Banco", objeto, self.obj("txt_03_1"),
                        self.obj("txt_03_2"), self.obj("cmb_doc_banco"),
                        self.obj("txt_03_3"), self.obj("txt_03_4"))
                    self.comprobar_cheque(objeto)

            elif objeto == self.obj("txt_03_2"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocBanco + "'",
                    "Nro. de Documento del Banco", self.obj("txt_03"),
                    self.obj("txt_03_1"), objeto, self.obj("cmb_doc_banco"),
                    self.obj("txt_03_3"), self.obj("txt_03_4"))
                self.comprobar_cheque(objeto)

            elif objeto == self.obj("txt_04"):
                if Op.comprobar_numero(int, objeto, "Cód. de Titular", self.obj("barraestado")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Titular", objeto, self.obj("txt_04_1"),
                        self.obj("txt_04_2"), self.obj("cmb_doc_titular"))

            elif objeto == self.obj("txt_04_2"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocTitular + "'",
                    "Nro. de Documento del Titular", self.obj("txt_04"),
                    self.obj("txt_04_1"), objeto, self.obj("cmb_doc_titular"))

            elif objeto in (self.obj("txt_05"), self.obj("txt_06")):
                if len(self.obj("txt_05").get_text()) > 0 \
                and len(self.obj("txt_06").get_text()) > 0 \
                and Op.compara_fechas(self.nav.datos_conexion,
                "'" + self.fecha_emision + "'", ">", "'" + self.fecha_cobro + "'") == 1:
                    self.obj("btn_guardar").set_sensitive(False)
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "La Fecha de Emisión NO puede posterior a la Fecha de Cobro.")
                else:
                    self.obj("barraestado").push(0, "")

            elif objeto == self.obj("txt_07"):
                Op.comprobar_numero(float, objeto, "Monto del Cheque", self.obj("barraestado"))

    def comprobar_cheque(self, objeto):
        cheque = self.obj("txt_01").get_text()
        cuenta = self.obj("txt_02").get_text()
        banco = self.obj("txt_03").get_text()

        if len(cheque) > 0 and len(cuenta) > 0 and len(banco) > 0:
            # Al editar, comprueba que los valores son diferentes del original
            busq = "" if not self.editando else " AND " + self.nav.campoid + " <> " + self.cond

            Op.comprobar_unique(self.nav.datos_conexion,
                self.nav.tabla + "_s", "NroCheque", cheque + " AND " +
                "NroCuenta = '" + cuenta + "' AND idBanco = " + banco + busq,
                objeto, self.obj("btn_guardar"), self.obj("barraestado"),
                "El Cheque introducido ya ha sido registado.")

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
    celda2 = Op.celdas(1.0)

    col0 = Op.columnas("Cód. Cheque", celda0, 0, True, 100, 200)
    col0.set_sort_column_id(0)
    col1 = Op.columnas("Nro. Cheque", celda0, 1, True, 100, 200)
    col1.set_sort_column_id(1)
    col2 = Op.columnas("Nro. Cuenta", celda0, 2, True, 100, 200)
    col2.set_sort_column_id(2)
    col3 = Op.columnas("Cód. Banco", celda0, 3, True, 100, 200)
    col3.set_sort_column_id(3)
    col4 = Op.columnas("Tipo de Documento", celda1, 4, True, 150)
    col4.set_sort_column_id(4)
    col5 = Op.columnas("Nro. Documento", celda0, 5, True, 100, 200)
    col5.set_sort_column_id(5)
    col6 = Op.columnas("Razón Social", celda1, 6, True, 200)
    col6.set_sort_column_id(6)
    col7 = Op.columnas("Dirección Principal", celda1, 7, True, 200, 500)
    col7.set_sort_column_id(7)
    col8 = Op.columnas("Teléfono Principal", celda0, 8, True, 100, 300)
    col8.set_sort_column_id(8)
    col9 = Op.columnas("Cód. Titular", celda0, 9, True, 100, 200)
    col9.set_sort_column_id(9)
    col10 = Op.columnas("Tipo de Documento", celda1, 10, True, 150)
    col10.set_sort_column_id(10)
    col11 = Op.columnas("Nro. Documento", celda0, 11, True, 100, 200)
    col11.set_sort_column_id(11)
    col12 = Op.columnas("Razón Social", celda1, 12, True, 200)
    col12.set_sort_column_id(12)
    col13 = Op.columnas("Cód. Tipo", celda0, 13, True, 100, 200)
    col13.set_sort_column_id(13)
    col14 = Op.columnas("Tipo de Cheque", celda1, 14, True, 200)
    col14.set_sort_column_id(14)
    col15 = Op.columnas("Fecha de Emisión", celda1, 15, True, 100, 200)
    col15.set_sort_column_id(19)  # Para ordenarse usa la fila 19
    col16 = Op.columnas("Fecha de Cobro", celda1, 16, True, 100, 200)
    col16.set_sort_column_id(20)  # Para ordenarse usa la fila 20
    col17 = Op.columnas("Monto", celda2, 17, True, 100, 200)
    col17.set_sort_column_id(17)
    col18 = Op.columna_active("Anulado", 18)
    col18.set_sort_column_id(18)

    lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8,
        col9, col10, col11, col12, col13, col14, col15, col16, col17]
    for columna in lista:
        columna.connect('clicked', self.on_treeviewcolumn_clicked)
        self.obj("grilla").append_column(columna)
    self.obj("grilla").append_column(col18)

    self.obj("grilla").set_rules_hint(True)
    self.obj("grilla").set_search_column(1)
    self.obj("grilla").set_property('enable-grid-lines', 3)
    columna_buscar(self, 1)

    lista = ListStore(int, int, str, int, str, str, str, str, str,
        int, str, str, str, int, str, str, str, float, bool, str, str)
    self.obj("grilla").set_model(lista)
    self.obj("grilla").show()


def cargar_grilla(self):
    if self.campo_buscar in ("FechaEmision", "FechaCobro"):
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " BETWEEN '" + self.fecha_ini + "' AND '" + self.fecha_fin + "'"
    else:
        opcion = "" if len(self.obj("txt_buscar").get_text()) == 0 else \
        " WHERE " + self.campo_buscar + " LIKE '%" + self.obj("txt_buscar").get_text() + "%'"

    if self.obj("rad_act").get_active() or self.obj("rad_ina").get_active():
        anulado = "1" if self.obj("rad_act").get_active() else "0"
        opcion += " WHERE " if len(opcion) == 0 else " AND "
        opcion += "Anulado = " + anulado

    conexion = Op.conectar(self.datos_conexion)
    cursor = Op.consultar(conexion, self.campoid + ", NroCheque, NroCuenta, " +
        "idBanco, BancoTipoDocumento, BancoNroDocumento, BancoRazonSocial, " +
        "BancoDireccion, BancoTelefono, idTitular, TitularTipoDocumento, " +
        "TitularNroDocumento, TitularRazonSocial, idTipoCheque, TipoCheque, " +
        "FechaEmision, FechaCobro, Monto, Anulado", self.tabla + "_s",
        opcion + " ORDER BY " + self.campoid + " DESC")
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()  # Finaliza la conexión

    lista = self.obj("grilla").get_model()
    lista.clear()

    for i in range(0, cant):
        lista.append([datos[i][0], datos[i][1], datos[i][2], datos[i][3],
            datos[i][4], datos[i][5], datos[i][6], datos[i][7], datos[i][8],
            datos[i][9], datos[i][10], datos[i][11], datos[i][12],
            datos[i][13], datos[i][14], Cal.mysql_fecha(datos[i][15]),
            Cal.mysql_fecha(datos[i][16]), datos[i][17], datos[i][18],
            str(datos[i][15]), str(datos[i][16])])

    cant = str(cant) + " registro encontrado." if cant == 1 \
        else str(cant) + " registros encontrados."
    self.obj("barraestado").push(0, cant)


def columna_buscar(self, idcolumna):
    if idcolumna == 0:
        col, self.campo_buscar = "Cód. de Cheque", self.campoid
    elif idcolumna == 1:
        col, self.campo_buscar = "Nro. de Cheque", "NroCheque"
    elif idcolumna == 2:
        col, self.campo_buscar = "Nro. de Cuenta", "NroCuenta"
    elif idcolumna == 3:
        col, self.campo_buscar = "Cód. de Banco", "idBanco"
    elif idcolumna == 4:
        col, self.campo_buscar = "Tipo de Documento (Banco)", "BancoTipoDocumento"
    elif idcolumna == 5:
        col, self.campo_buscar = "Nro. de Documento (Banco)", "BancoNroDocumento"
    elif idcolumna == 6:
        col, self.campo_buscar = "Razón Social (Banco)", "BancoRazonSocial"
    elif idcolumna == 7:
        col, self.campo_buscar = "Dirección (Banco)", "BancoDireccion"
    elif idcolumna == 8:
        col, self.campo_buscar = "Teléfono (Banco)", "BancoTelefono"
    elif idcolumna == 9:
        col, self.campo_buscar = "Cód. de Titular", "idTitular"
    elif idcolumna == 10:
        col, self.campo_buscar = "Tipo de Documento (Titular)", "TitularTipoDocumento"
    elif idcolumna == 11:
        col, self.campo_buscar = "Nro. de Documento (Titular)", "TitularNroDocumento"
    elif idcolumna == 12:
        col, self.campo_buscar = "Razón Social (Titular)", "TitularRazonSocial"
    elif idcolumna == 13:
        col, self.campo_buscar = "Cód. de Tipo", "idTipoCheque"
    elif idcolumna == 14:
        col, self.campo_buscar = "Tipo de Cheque", "TipoCheque"
    elif idcolumna == 19:
        col, self.campo_buscar = "Fecha de Emisión", "FechaEmision"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 20:
        col, self.campo_buscar = "Fecha de Cobro", "FechaCobro"
        self.obj("txt_buscar").set_editable(False)
        self.obj("hbox_fecha").set_visible(True)
    elif idcolumna == 17:
        col, self.campo_buscar = "Monto del Cheque", "Monto"

    self.obj("label_buscar").set_text("Filtrar por " + col + ":")


def eliminar(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    anulado = seleccion.get_value(iterador, 18)

    if anulado != 1:
        valor0 = str(seleccion.get_value(iterador, 0))
        valor1 = str(seleccion.get_value(iterador, 1))
        valor2 = seleccion.get_value(iterador, 2)
        valor3 = seleccion.get_value(iterador, 6)
        valor4 = seleccion.get_value(iterador, 12)
        valor5 = seleccion.get_value(iterador, 15)
        valor6 = seleccion.get_value(iterador, 16)

        eleccion = Mens.pregunta_anular("Seleccionó:\n" +
            "\nNro. Cheque: " + valor1 + "\nNro. Cuenta: " + valor2 +
            "\nBanco: " + valor3 + "\nTitular: " + valor4 +
            "\nFecha de Emisión: " + valor5 + "\nFecha de Cobro: " + valor6)

        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        if eleccion:
            conexion = Op.conectar(self.datos_conexion)
            Op.anular(conexion, self.tabla, valor0)
            conexion.commit()
            conexion.close()  # Finaliza la conexión
            cargar_grilla(self)
    else:
        self.obj("barraestado").push(0, "NO puede Anular un Cheque que ya ha sido Anulado.")


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

    lista = [[Par("Nro. Cheque", head), Par("Banco", head), Par("Titular", head),
        Par("Fecha de Emisión", head), Par("Fecha de Cobro", head), Par("Monto", head)]]

    for i in range(0, cant):
        lista.append([Par(str(datos[i][1]), body_ce), Par(datos[i][6], body_iz),
            Par(datos[i][12], body_iz), Par(datos[i][15], body_ce),
            Par(datos[i][16], body_ce), Par(str(datos[i][17]), body_de)])

    listado.listado(self.titulo, lista, [100, 150, 150, 110, 110, 70], landscape(A4))


def seleccion(self):
    seleccion, iterador = self.obj("grilla").get_selection().get_selected()
    anulado = seleccion.get_value(iterador, 15)

    if anulado != 1:  # No puede estar Anulado
        try:
            valor0 = seleccion.get_value(iterador, 0)
            valor1 = str(seleccion.get_value(iterador, 1))
            valor2 = seleccion.get_value(iterador, 2)

            valor3 = str(seleccion.get_value(iterador, 3))  # Banco
            valor4 = seleccion.get_value(iterador, 4)
            valor5 = seleccion.get_value(iterador, 5)
            valor6 = seleccion.get_value(iterador, 6)
            valor7 = seleccion.get_value(iterador, 7)
            valor8 = seleccion.get_value(iterador, 8)

            valor7 = "" if valor7 is None else valor7
            valor8 = "" if valor8 is None else valor8

            valor9 = str(seleccion.get_value(iterador, 9))  # Titular
            valor10 = seleccion.get_value(iterador, 10)
            valor11 = seleccion.get_value(iterador, 11)
            valor12 = seleccion.get_value(iterador, 12)

            valor13 = seleccion.get_value(iterador, 17)

            self.origen.cod_cheque = valor0
            self.origen.txt_nro_chq.set_text(valor1)
            self.origen.txt_nro_cta.set_text(valor2)

            # Asignación de Tipo de Documento (Banco) en Combo
            model, i = self.origen.cmb_doc_ban.get_model(), 0
            while model[i][0] != valor4: i += 1
            self.origen.cmb_doc_ban.set_active(i)

            self.origen.txt_cod_ban.set_text(valor3)
            self.origen.txt_scl_ban.set_text(valor6)
            self.origen.txt_doc_ban.set_text(valor5)
            self.origen.txt_dir_ban.set_text(valor7)
            self.origen.txt_tel_ban.set_text(valor8)

            # Asignación de Tipo de Documento (Titular) en Combo
            model, i = self.origen.cmb_doc_tit.get_model(), 0
            while model[i][0] != valor10: i += 1
            self.origen.cmb_doc_tit.set_active(i)

            self.origen.txt_cod_tit.set_text(valor9)
            self.origen.txt_scl_tit.set_text(valor12)
            self.origen.txt_doc_tit.set_text(valor11)

            self.origen.txt_monto.set_text(str(valor13))
            self.origen.monto_cheque = valor13

            self.on_btn_salir_clicked(0)
        except:
            pass
    else:
        self.obj("barraestado").push(0, "NO puede seleccionar un Cheque que ha sido Anulado.")
