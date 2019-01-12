#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
from gi.repository.Gtk import ListStore
from gi.repository.Gdk import ModifierType
from clases import mensajes as Mens
from clases import operaciones as Op


class cobros:

    def __init__(self, datos, con, tab, total, nro, timb=None):
        self.datos_conexion = datos
        self.conexion = con
        self.tabla = tab

        cursor = self.conexion.cursor()
        cursor.execute("SAVEPOINT cobros")
        cursor.close()

        arch = Op.archivo("venta_cobros")
        self.obj = arch.get_object

        self.obj("ventana").set_default_size(775, 600)
        self.obj("ventana").set_position(1)
        self.obj("ventana").set_modal(True)

        self.obj("ventana").set_title("Cobros por Forma de Pago/Cobro")

        self.obj("btn_cheque").set_tooltip_text("Presione este botón para buscar datos de un Cheque de Tercero")
        self.obj("btn_moneda").set_tooltip_text("Presione este botón para buscar datos de una Moneda")
        self.obj("btn_tarjeta").set_tooltip_text("Presione este botón para buscar datos de una Tarjeta")

        self.obj("btn_ch_banco").set_tooltip_text("Presione este botón para buscar datos de una Entidad Financiera")
        self.obj("btn_ch_titular").set_tooltip_text("Presione este botón para buscar datos del Titular del Cheque")
        self.obj("btn_tj_banco").set_tooltip_text("Presione este botón para buscar datos de una Entidad Financiera")
        self.obj("btn_tj_titular").set_tooltip_text("Presione este botón para buscar datos del Titular de la Tarjeta")

        self.obj("btn_nuevo").set_tooltip_text("Presione este botón para agregar un nuevo Cobro por Cheque o Tarjeta")
        self.obj("btn_modificar").set_tooltip_text("Presione este botón para modificar datos de un Cobro por Cheque o Tarjeta")
        self.obj("btn_eliminar").set_tooltip_text("Presione este botón para eliminar un Cobro por Cheque o Tarjeta")

        Op.combos_config(self.datos_conexion, self.obj("cmb_ch_banco"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.datos_conexion, self.obj("cmb_ch_titular"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.datos_conexion, self.obj("cmb_tj_banco"), "tipodocumentos", "idTipoDocumento")
        Op.combos_config(self.datos_conexion, self.obj("cmb_tj_titular"), "tipodocumentos", "idTipoDocumento")

        self.obj("txt_00").set_text(nro)
        self.obj("txt_total").set_text(total)

        if timb is None:
            self.obj("label1").set_text("Nro. Recibo:")
            self.obj("label2").set_visible(False)
            self.obj("txt_01").set_visible(False)
        else:
            self.obj("txt_01").set_text(timb)

        self.txt_nro_chq, self.txt_nro_cta = self.obj("txt_ch_00"), self.obj("txt_ch_01")
        self.txt_monto = self.obj("txt_ch_04")
        self.txt_cod_mon, self.txt_des_mon = self.obj("txt_md_00"), self.obj("txt_md_00_1")
        self.txt_cot_vent = self.obj("txt_md_02")
        self.txt_nro_tj = self.obj("txt_tj_00")

        self.cod_cheque = -1
        self.monto_cheque = 0  # Valor Total del Cheque registrado
        self.monto_ch_doc = 0  # Valor del Cheque para Factura o Recibo (al Editar)
        self.monto_md_doc = 0  # Valor del Efectivo para Factura o Recibo (al Editar)
        self.monto_tj_doc = 0  # Valor de la Tarjeta para Factura o Recibo (al Editar)

        self.estadocobros(False)
        self.config_grilla_detalles()
        self.cargar_grilla_detalles()

        arch.connect_signals(self)
        self.obj("ventana").show()

    def on_btn_guardar_clicked(self, objeto):
        self.obj("ventana").destroy()

    def on_btn_cancelar_clicked(self, objeto):
        cursor = self.conexion.cursor()
        cursor.execute("ROLLBACK TO SAVEPOINT cobros")
        cursor.close()

        self.obj("ventana").destroy()

    def estadocobros(self, estado):
        self.obj("notebook").set_visible(estado)
        self.obj("hbuttonbox2").set_visible(estado)

        self.obj("separador1").set_visible(not estado)
        self.obj("hbuttonbox1").set_sensitive(not estado)
        self.obj("grilla").set_sensitive(not estado)
        self.obj("btn_guardar").set_sensitive(not estado)
        self.obj("btn_cancelar").set_sensitive(not estado)

    def estadoedicion(self, estado):
        self.obj("notebook").set_show_tabs(estado)

        self.obj("hbox4").set_sensitive(estado)
        self.obj("hbox7").set_sensitive(estado)
        self.obj("hbox8").set_sensitive(estado)
        self.obj("hbox9").set_sensitive(estado)
        self.obj("hbox10").set_sensitive(estado)
        self.obj("hbox11").set_sensitive(estado)

        self.obj("hbox13").set_sensitive(estado)

        self.obj("hbox18").set_sensitive(estado)
        self.obj("hbox19").set_sensitive(estado)
        self.obj("hbox20").set_sensitive(estado)
        self.obj("hbox21").set_sensitive(estado)
        self.obj("hbox22").set_sensitive(estado)
        self.obj("hbox23").set_sensitive(estado)

##### Formas de Cobro ##################################################

    def config_grilla_detalles(self):
        celda0 = Op.celdas(1.0)
        celda1 = Op.celdas(0.0)

        col0 = Op.columnas("Forma de Cobro", celda1, 0, True, 100)
        col0.set_sort_column_id(0)
        col1 = Op.columnas("Número", celda0, 1, True, 125)
        col1.set_sort_column_id(1)
        col2 = Op.columnas("Razón Social del Titular", celda1, 2, True, 170)
        col2.set_sort_column_id(2)
        col3 = Op.columnas("R.U.C. Banco", celda0, 3, True, 90)
        col3.set_sort_column_id(3)
        col4 = Op.columnas("Razón Social del Banco", celda1, 4, True, 170)
        col4.set_sort_column_id(4)
        col5 = Op.columnas("Moneda", celda1, 5, True, 170)
        col5.set_sort_column_id(5)
        col6 = Op.columnas("Cantidad", celda0, 6, False, 90)
        col6.set_sort_column_id(6)
        col7 = Op.columnas("Cotización", celda0, 7, False, 90)
        col7.set_sort_column_id(7)
        col8 = Op.columnas("Monto", celda0, 8, False, 90)
        col8.set_sort_column_id(8)

        lista = [col0, col1, col2, col3, col4, col5, col6, col7, col8]
        for columna in lista:
            columna.connect('clicked', self.on_treeviewcolumn_clicked)
            self.obj("grilla").append_column(columna)

        self.obj("grilla").set_rules_hint(True)
        self.obj("grilla").set_search_column(0)
        self.obj("grilla").set_property('enable-grid-lines', 3)

        lista = ListStore(str, str, str, str, str, str, str, str, float,
            str, str, str)
        self.obj("grilla").set_model(lista)
        self.obj("grilla").show()

    def cargar_grilla_detalles(self):
        monto = Decimal(0.0)
        lista = self.obj("grilla").get_model()
        lista.clear()

        if self.obj("txt_01").get_visible():  # Factura de Venta
            condicion = "NroTimbrado = " + self.obj("txt_01").get_text() + \
                " AND NroFactura = " + self.obj("txt_00").get_text()
        else:  # Recibos
            condicion = "NroRecibo = " + self.obj("txt_00").get_text()

        # Cargar datos de Cheques de Terceros
        cursor = Op.consultar(self.conexion, "NroCheque, TitularRazonSocial, " +
            "BancoNroDocumento, BancoRazonSocial, MontoCobrado, idChequeTercero, " +
            "idBanco, NroCuenta", self.tabla + "_chequeterceros_s",
            " WHERE " + condicion + " ORDER BY NroCheque")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        for i in range(0, cant):
            monto += Decimal(datos[i][4])
            lista.append(["Cheque", str(datos[i][0]), datos[i][1],
                datos[i][2], datos[i][3], None, None, None, datos[i][4],
                str(datos[i][5]), str(datos[i][6]), datos[i][7]])  # Ocultos

        cant_registros = cant

        # Cargar datos de Tarjetas de Crédito y Débito
        cursor = Op.consultar(self.conexion, "NroTarjeta, " +
            "TitularRazonSocial, BancoNroDocumento, BancoRazonSocial, Monto",
            self.tabla + "_tarjetas_s", " WHERE " + condicion +
            " ORDER BY NroTarjeta")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        for i in range(0, cant):
            monto += Decimal(datos[i][4])
            lista.append(["Tarjeta", datos[i][0], datos[i][1],
                datos[i][2], datos[i][3], None, None, None, datos[i][4],
                None, None, None])  # Ocultos

        cant_registros += cant

        # Cargar datos de Cobro en Efectivo
        cursor = Op.consultar(self.conexion, "Moneda, Monto, Cotizacion, " +
            "MontoGuaranies, idMoneda", self.tabla + "_monedas_s",
            " WHERE " + condicion + " ORDER BY idMoneda")
        datos = cursor.fetchall()
        cant = cursor.rowcount

        for i in range(0, cant):
            monto += Decimal(datos[i][3])
            lista.append(["Efectivo", None, None, None, None,
                datos[i][0], str(datos[i][1]), str(datos[i][2]), datos[i][3],
                str(datos[i][4]), None, None])  # Ocultos

        cant_registros += cant

        # Cargar datos de Monto Disponible
        self.monto_efectivo = Decimal(self.obj("txt_total").get_text()) - monto
        self.obj("txt_disponible").set_text(str(self.monto_efectivo))

        cant = str(cant_registros) + " registro encontrado." if cant_registros == 1 \
            else str(cant_registros) + " registros encontrados."
        self.obj("barraestado").push(0, cant)

    def on_btn_nuevo_clicked(self, objeto):
        if self.monto_efectivo > 0:
            self.editando_cobro = False
            self.funcion_cobros()
        else:
            self.obj("barraestado").push(0, "Ya no es posible asignar ningún valor a otra forma de cobro.")

    def on_btn_modificar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            tipo = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Modificar.")
        else:
            self.editando_cobro = True
            self.funcion_cobros()

    def on_btn_eliminar_clicked(self, objeto):
        try:
            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            tipo = seleccion.get_value(iterador, 0)
        except:
            self.obj("barraestado").push(0, "Seleccione un registro de la lista. Luego presione Eliminar.")
        else:
            condicion = self.obj("txt_00").get_text() if self.tabla == "recibos" \
            else self.obj("txt_01").get_text() + ", " + self.obj("txt_00").get_text()

            numero = seleccion.get_value(iterador, 1)
            titular = seleccion.get_value(iterador, 2)
            banco = seleccion.get_value(iterador, 4)
            moneda = seleccion.get_value(iterador, 5)
            cant = seleccion.get_value(iterador, 6)
            cotiz = seleccion.get_value(iterador, 7)
            monto = str(seleccion.get_value(iterador, 8))
            codigo = seleccion.get_value(iterador, 9)

            if tipo == "Efectivo":
                mensaje = "Seleccionó:\n\nMoneda: " + moneda + \
                    "\nCantidad: " + cant + "\nCotización: " + cotiz + \
                    "\nMonto: " + monto
            else:
                mensaje = "Seleccionó:\n\nNúmero: " + numero + \
                    "\nBanco: " + banco + "\nTitular: " + titular + \
                    "\nMonto: " + monto

            eleccion = Mens.pregunta_borrar(mensaje)
            self.obj("grilla").get_selection().unselect_all()
            self.obj("barraestado").push(0, "")

            if eleccion:
                if tipo == "Cheque":
                    Op.eliminar(self.conexion, self.tabla + "_chequeterceros",
                        condicion + ", " + codigo)

                elif tipo == "Efectivo":
                    Op.eliminar(self.conexion, self.tabla + "_monedas",
                        condicion + ", " + codigo)

                elif tipo == "Tarjeta":
                    Op.eliminar(self.conexion, self.tabla + "_tarjetas",
                        condicion + ", '" + numero + "'")

                self.cargar_grilla_detalles()

    def on_grilla_row_activated(self, objeto, fila, col):
        self.on_btn_modificar_clicked(0)

    def on_grilla_key_press_event(self, objeto, evento):
        if evento.keyval == 65535:  # Presionando Suprimir (Delete)
            self.on_btn_eliminar_clicked(0)

    def on_treeviewcolumn_clicked(self, objeto):
        i = objeto.get_sort_column_id()
        self.obj("grilla").set_search_column(i)

##### Agregar-Modificar Formas de Cobro ################################

    def funcion_cobros(self):
        if self.editando_cobro:
            if self.tabla == "recibos":
                condicion = "NroRecibo = " + self.obj("txt_00").get_text()
            else:
                condicion = "NroTimbrado = " + self.obj("txt_01").get_text() + \
                    " AND NroFactura = " + self.obj("txt_00").get_text()

            seleccion, iterador = self.obj("grilla").get_selection().get_selected()
            tipo = seleccion.get_value(iterador, 0)
            numero = seleccion.get_value(iterador, 1)
            moneda = seleccion.get_value(iterador, 5)
            cant = str(seleccion.get_value(iterador, 6))
            cotiz = str(seleccion.get_value(iterador, 7))
            monto = seleccion.get_value(iterador, 8)
            codigo = seleccion.get_value(iterador, 9)
            banco = str(seleccion.get_value(iterador, 10))
            cuenta = seleccion.get_value(iterador, 11)

            if tipo == "Cheque":
                self.obj("notebook").set_current_page(0)
                self.obj("txt_ch_00").set_text(str(numero))
                self.obj("txt_ch_01").set_text(cuenta)
                self.obj("txt_ch_02").set_text(banco)
                self.obj("txt_ch_04").set_text(str(monto))

                self.focus_out_event(self.obj("txt_ch_00"), 0)
                self.monto_ch_doc = Decimal(monto)

            elif tipo == "Efectivo":
                self.obj("notebook").set_current_page(1)
                self.obj("txt_md_00").set_text(str(codigo))
                self.obj("txt_md_00_1").set_text(moneda)
                self.obj("txt_md_01").set_text(cant)
                self.obj("txt_md_02").set_text(cotiz)
                self.obj("txt_md_03").set_text(str(monto))
                self.monto_md_doc = Decimal(monto)

            else:  # Tarjeta
                self.obj("notebook").set_current_page(2)
                self.obj("txt_tj_00").set_text(numero)
                self.obj("txt_tj_03").set_text(str(monto))

                self.focus_out_event(self.obj("txt_tj_00"), 0)
                self.monto_tj_doc = Decimal(monto)

            self.estadoedicion(False)
        else:
            self.estadoedicion(True)
            self.obj("notebook").set_current_page(2)
            self.obj("txt_tj_00").grab_focus()

        self.obj("grilla").get_selection().unselect_all()
        self.obj("barraestado").push(0, "")

        self.obj("btn_guardar_cobro").set_sensitive(False)
        self.estadocobros(True)

    def on_btn_guardar_cobro_clicked(self, objeto):
        condicion = self.obj("txt_00").get_text() if self.tabla == "recibos" \
            else self.obj("txt_01").get_text() + ", " + self.obj("txt_00").get_text()
        page = self.obj("notebook").get_current_page()

        if page == 0:  # Guardando Cheques de Terceros
            monto = self.obj("txt_ch_04").get_text()

            sql = condicion + ", " + str(self.cod_cheque) + ", " + monto

            if not self.editando_cobro:
                Op.insertar(self.conexion, self.tabla + "_chequeterceros", sql)
            else:
                Op.modificar(self.conexion, self.tabla + "_chequeterceros", sql)

        elif page == 1:  # Guardando Cobro en Efectivo
            moneda = self.obj("txt_md_00").get_text()
            cant = self.obj("txt_md_01").get_text()
            cotiz = self.obj("txt_md_02").get_text()

            sql = condicion + ", " + moneda + ", " + cotiz + ", " + cant

            if not self.editando_cobro:
                Op.insertar(self.conexion, self.tabla + "_monedas", sql)
            else:
                Op.modificar(self.conexion, self.tabla + "_monedas", sql)

        else:  # Guardando Tarjetas
            tarjeta = self.obj("txt_tj_00").get_text()
            monto = self.obj("txt_tj_03").get_text()

            sql = condicion + ", '" + tarjeta + "', " + monto

            if not self.editando_cobro:
                Op.insertar(self.conexion, self.tabla + "_tarjetas", sql)
            else:
                Op.modificar(self.conexion, self.tabla + "_tarjetas", sql)

        self.cargar_grilla_detalles()
        self.on_btn_cancelar_cobro_clicked(0)

    def on_btn_cancelar_cobro_clicked(self, objeto):
        self.obj("txt_ch_00").set_text("")
        self.obj("txt_ch_01").set_text("")
        self.obj("txt_ch_02").set_text("")
        self.obj("txt_ch_02_1").set_text("")
        self.obj("txt_ch_02_2").set_text("")
        self.obj("cmb_ch_banco").set_active(-1)
        self.obj("txt_ch_02_3").set_text("")
        self.obj("txt_ch_02_4").set_text("")
        self.obj("txt_ch_03").set_text("")
        self.obj("txt_ch_03_1").set_text("")
        self.obj("txt_ch_03_2").set_text("")
        self.obj("cmb_ch_titular").set_active(-1)
        self.obj("txt_ch_04").set_text("")

        self.obj("txt_md_00").set_text("")
        self.obj("txt_md_00_1").set_text("")
        self.obj("txt_md_01").set_text("")
        self.obj("txt_md_02").set_text("")
        self.obj("txt_md_03").set_text("")

        self.obj("txt_tj_00").set_text("")
        self.obj("txt_tj_01").set_text("")
        self.obj("txt_tj_01_1").set_text("")
        self.obj("txt_tj_01_2").set_text("")
        self.obj("cmb_tj_banco").set_active(-1)
        self.obj("txt_tj_01_3").set_text("")
        self.obj("txt_tj_01_4").set_text("")
        self.obj("txt_tj_02").set_text("")
        self.obj("txt_tj_02_1").set_text("")
        self.obj("txt_tj_02_2").set_text("")
        self.obj("cmb_tj_titular").set_active(-1)
        self.obj("txt_tj_03").set_text("")

        self.cod_cheque = -1
        self.monto_cheque = self.monto_ch_doc = self.monto_md_doc = self.monto_tj_doc = 0
        self.estadocobros(False)

    def verificacion(self, objeto):
        page = self.obj("notebook").get_current_page()
        if page == 0:
            # Verificando Cheques de Terceros
            if len(self.obj("txt_ch_00").get_text()) == 0 or len(self.obj("txt_ch_01").get_text()) == 0 \
            or len(self.obj("txt_ch_02").get_text()) == 0 or len(self.obj("txt_ch_02_1").get_text()) == 0 \
            or len(self.obj("txt_ch_03").get_text()) == 0 or len(self.obj("txt_ch_03_1").get_text()) == 0 \
            or len(self.obj("txt_ch_04").get_text()) == 0 or self.idTipoDocBancoCheque == -1 \
            or self.idTipoDocTitularCheque == -1:
                estado = False
            else:
                estado = True

        elif page == 1:
            # Verificando Cobros en Efectivo
            if len(self.obj("txt_md_00").get_text()) == 0 or len(self.obj("txt_md_01").get_text()) == 0 \
            or len(self.obj("txt_md_02").get_text()) == 0 or len(self.obj("txt_md_03").get_text()) == 0:
                estado = False
            else:
                estado = True

        else: # Verificando Tarjetas
            if len(self.obj("txt_tj_00").get_text()) == 0 or len(self.obj("txt_tj_01").get_text()) == 0 \
            or len(self.obj("txt_tj_01_1").get_text()) == 0 or len(self.obj("txt_tj_02").get_text()) == 0 \
            or len(self.obj("txt_tj_02_1").get_text()) == 0 or len(self.obj("txt_tj_03").get_text()) == 0 \
            or self.idTipoDocBancoTarjeta == -1 or self.idTipoDocTitularTarjeta == -1:
                estado = False
            else:
                estado = True
        self.obj("btn_guardar_cobro").set_sensitive(estado)

    def on_cmb_tipo_doc_changed(self, objeto):
        model = objeto.get_model()
        active = objeto.get_active()

        if active > -1:
            if objeto == self.obj("cmb_ch_banco"):
                self.idTipoDocBancoCheque = model[active][0]
                self.focus_out_event(self.obj("txt_ch_02_2"), 0)  # Nro. Documento

            elif objeto == self.obj("cmb_ch_titular"):
                self.idTipoDocTitularCheque = model[active][0]
                self.focus_out_event(self.obj("txt_ch_03_2"), 0)  # Nro. Documento

            elif objeto == self.obj("cmb_tj_banco"):
                self.idTipoDocBancoTarjeta = model[active][0]
                self.focus_out_event(self.obj("txt_tj_01_2"), 0)  # Nro. Documento

            elif objeto == self.obj("cmb_tj_titular"):
                self.idTipoDocTitularTarjeta = model[active][0]
                self.focus_out_event(self.obj("txt_ch_02_2"), 0)  # Nro. Documento
        else:
            self.obj("barraestado").push(0, "No existen registros de Tipos de Documentos de Identidad en el Sistema.")

    def key_press_event(self, objeto, evento):
        if evento.state & ModifierType.CONTROL_MASK:  # Tecla CTRL en combinación
            if evento.keyval == 65293:  # Presionando Enter
                if objeto in (self.obj("txt_ch_00"), self.obj("txt_ch_01")):
                    self.on_btn_cheque_clicked(0)
                elif objeto in (self.obj("txt_ch_02"), self.obj("txt_ch_02_2")):
                    self.on_btn_ch_banco_clicked(0)
                elif objeto in (self.obj("txt_ch_03"), self.obj("txt_ch_03_2")):
                    self.on_btn_ch_titular_clicked(0)

                elif objeto == self.obj("txt_md_00"):
                    self.on_btn_moneda_clicked(0)

                elif objeto == self.obj("txt_tj_00"):
                    self.on_btn_tarjeta_clicked(0)
                elif objeto in (self.obj("txt_tj_01"), self.obj("txt_tj_01_2")):
                    self.on_btn_tj_banco_clicked(0)
                elif objeto in (self.obj("txt_tj_02"), self.obj("txt_tj_02_2")):
                    self.on_btn_tj_titular_clicked(0)
        elif evento.keyval == 65293:  # Presionando Enter
            self.focus_out_event(objeto, 0)

    def focus_in_event(self, objeto, evento):
        if objeto in (self.obj("txt_ch_00"), self.obj("txt_ch_01")):
            texto = " Cheque de Tercero"
        elif objeto == self.obj("txt_md_00"):
            texto = "a Moneda"
        elif objeto == self.obj("txt_tj_00"):
            texto = "a Tarjeta"
        elif objeto in (self.obj("txt_ch_02"), self.obj("txt_ch_02_2"),
        self.obj("txt_tj_01"), self.obj("txt_tj_01_2")):
            texto = " Banco"
        elif objeto in (self.obj("txt_ch_03"), self.obj("txt_ch_03_2"),
        self.obj("txt_tj_02"), self.obj("txt_tj_02_2")):
            texto = " Titular"
        self.obj("barraestado").push(0, "Presione CTRL + Enter para Buscar un" + texto + ".")

    def focus_out_event(self, objeto, evento):
        valor = objeto.get_text()
        if len(valor) == 0:
            self.obj("barraestado").push(0, "")

            if objeto == self.obj("txt_ch_02"):  # Código de Banco (Cheque)
                self.obj("txt_ch_02_1").set_text("")
                self.obj("txt_ch_02_2").set_text("")
                self.obj("txt_ch_02_3").set_text("")
                self.obj("txt_ch_02_4").set_text("")
            elif objeto == self.obj("txt_ch_02_2") and len(self.obj("txt_ch_02").get_text()) == 0:
                self.obj("txt_ch_02_1").set_text("")
                self.obj("txt_ch_02_3").set_text("")
                self.obj("txt_ch_02_4").set_text("")
            elif objeto == self.obj("txt_ch_03"):  # Código de Titular (Cheque)
                self.obj("txt_ch_03_1").set_text("")
                self.obj("txt_ch_03_2").set_text("")
            elif objeto == self.obj("txt_ch_03_2") and len(self.obj("txt_ch_03").get_text()) == 0:
                self.obj("txt_ch_03_1").set_text("")

            elif objeto == self.obj("txt_md_00"):  # Código de Moneda
                self.obj("txt_md_00_1").set_text("")
                self.obj("txt_md_02").set_text("1.0")

            elif objeto == self.obj("txt_tj_01"):  # Código de Banco (Tarjeta)
                self.obj("txt_tj_01_1").set_text("")
                self.obj("txt_tj_01_2").set_text("")
                self.obj("txt_tj_01_3").set_text("")
                self.obj("txt_tj_01_4").set_text("")
            elif objeto == self.obj("txt_tj_01_2") and len(self.obj("txt_tj_01").get_text()) == 0:
                self.obj("txt_tj_01_1").set_text("")
                self.obj("txt_tj_01_3").set_text("")
                self.obj("txt_tj_01_4").set_text("")
            elif objeto == self.obj("txt_tj_02"):  # Código de Titular (Tarjeta)
                self.obj("txt_tj_02_1").set_text("")
                self.obj("txt_tj_02_2").set_text("")
            elif objeto == self.obj("txt_tj_02_2") and len(self.obj("txt_tj_02").get_text()) == 0:
                self.obj("txt_tj_02_1").set_text("")
        else:
            if objeto in (self.obj("txt_ch_00"), self.obj("txt_ch_01")):
                if len(self.obj("txt_ch_00").get_text()) > 0 \
                and len(self.obj("txt_ch_01").get_text()) > 0 \
                and len(self.obj("txt_ch_02").get_text()) > 0:
                    conexion = Op.conectar(self.datos_conexion)
                    cursor = Op.consultar(conexion, "BancoRazonSocial, " +
                        "BancoNroDocumento, BancoTipoDocumento, BancoDireccion, " +
                        "BancoTelefono, idTitular, TitularRazonSocial, " +
                        "TitularNroDocumento, TitularTipoDocumento, " +
                        "idChequeTercero, Monto", "chequeterceros_s",
                        " WHERE NroCheque = " + self.obj("txt_ch_00").get_text() +
                        " AND NroCuenta = '" + self.obj("txt_ch_01").get_text() + "'" +
                        " AND idBanco = " + self.obj("txt_ch_02").get_text())
                    datos = cursor.fetchall()
                    cant = cursor.rowcount
                    conexion.close()  # Finaliza la conexión

                    if cant > 0:
                        direccion = "" if datos[0][3] is None else datos[0][3]
                        telefono = "" if datos[0][4] is None else datos[0][4]

                        self.obj("txt_ch_02_1").set_text(datos[0][0])
                        self.obj("txt_ch_02_2").set_text(datos[0][1])
                        self.obj("txt_ch_02_3").set_text(direccion)
                        self.obj("txt_ch_02_4").set_text(telefono)

                        # Asignación de Tipo de Documento (Banco) en Combo
                        model, i = self.obj("cmb_ch_banco").get_model(), 0
                        while model[i][0] != datos[0][2]: i += 1
                        self.obj("cmb_ch_banco").set_active(i)

                        self.obj("txt_ch_03").set_text(str(datos[0][5]))
                        self.obj("txt_ch_03_1").set_text(datos[0][6])
                        self.obj("txt_ch_03_2").set_text(datos[0][7])

                        # Asignación de Tipo de Documento (Titular) en Combo
                        model, i = self.obj("cmb_ch_titular").get_model(), 0
                        while model[i][0] != datos[0][8]: i += 1
                        self.obj("cmb_ch_titular").set_active(i)

                        self.cod_cheque, self.monto_cheque = datos[0][9], datos[0][10]
                        self.obj("barraestado").push(0, "")
                        self.verificacion(0)

                        # Verificar que el Cheque NO haya sido utilizado en otra Factura
                        if Op.comprobar_unique(self.datos_conexion,
                        "facturaventas_chequeterceros_s", "idChequeTercero",
                        str(self.cod_cheque), self.obj("txt_ch_00"),
                        self.obj("btn_guardar_cobro"), self.obj("barraestado"),
                        "El Cheque introducido ya ha sido utilizado en otro Cobro (Factura)."):
                            # Verificar que el Cheque NO haya sido utilizado en otro Recibo
                            # si no se ha utilizado en otra Factura
                            Op.comprobar_unique(self.datos_conexion,
                            "recibos_chequeterceros_s", "idChequeTercero",
                            str(self.cod_cheque), self.obj("txt_ch_00"),
                            self.obj("btn_guardar_cobro"), self.obj("barraestado"),
                            "El Cheque introducido ya ha sido utilizado en otro Cobro (Recibo).")
                    else:
                        self.obj("btn_guardar_cobro").set_sensitive(False)
                        self.obj("txt_ch_00").grab_focus()
                        self.obj("barraestado").push(0, "El Cheque introducido no es válido (NO ESTÁ REGISTRADO).")

            elif objeto == self.obj("txt_ch_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Banco", self.obj("barraestado")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Banco", objeto, self.obj("txt_ch_02_1"),
                        self.obj("txt_ch_02_2"), self.obj("cmb_ch_banco"),
                        self.obj("txt_ch_02_3"), self.obj("txt_ch_02_4"))
                    self.focus_out_event(self.obj("txt_ch_00"), 0)

            elif objeto == self.obj("txt_ch_02_2"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocBancoCheque + "'",
                    "Nro. de Documento del Banco", self.obj("txt_ch_02"),
                    self.obj("txt_ch_02_1"), objeto, self.obj("cmb_ch_banco"),
                    self.obj("txt_ch_02_3"), self.obj("txt_ch_02_4"))
                self.focus_out_event(self.obj("txt_ch_00"), 0)

            elif objeto == self.obj("txt_ch_03"):
                if Op.comprobar_numero(int, objeto, "Cód. de Titular", self.obj("barraestado")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Titular", objeto, self.obj("txt_ch_03_1"),
                        self.obj("txt_ch_03_2"), self.obj("cmb_ch_titular"))

            elif objeto == self.obj("txt_ch_03_2"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocTitularCheque + "'",
                    "Nro. de Documento del Titular", self.obj("txt_ch_03"),
                    self.obj("txt_ch_03_1"), objeto, self.obj("cmb_ch_titular"))

            elif objeto == self.obj("txt_ch_04"):
                if Op.comprobar_numero(float, objeto, "Monto a Cobrar (Cheque)", self.obj("barraestado")):
                    self.comprobar_valor_monto(objeto, Decimal(valor))

            elif objeto == self.obj("txt_md_00"):
                conexion = Op.conectar(self.datos_conexion)
                cursor = Op.consultar(conexion, "Nombre, Venta",
                    "monedas_s", " WHERE idMoneda = " + valor)
                datos = cursor.fetchall()
                cant = cursor.rowcount
                conexion.close()  # Finaliza la conexión

                if cant > 0:
                    self.obj("txt_md_00_1").set_text(datos[0][0])
                    self.obj("txt_md_02").set_text(str(datos[0][1]))
                    self.obj("barraestado").push(0, "")
                    self.verificacion(0)
                else:
                    self.obj("btn_guardar_cobro").set_sensitive(False)
                    self.obj("txt_md_00").grab_focus()
                    self.obj("barraestado").push(0, "El Cód. de Moneda introducido no es válido.")

            elif objeto == self.obj("txt_md_01"):
                if Op.comprobar_numero(float, objeto, "Monto a Cobrar (Moneda)", self.obj("barraestado")):
                    cotizacion = self.obj("txt_md_02").get_text()
                    if len(cotizacion) > 0:
                        monto = round(Decimal(valor) * Decimal(cotizacion), 2)
                        self.obj("txt_md_03").set_text(str(monto))
                        self.comprobar_valor_monto(self.obj("txt_md_01"), monto)

            elif objeto == self.obj("txt_md_02"):
                if Op.comprobar_numero(float, objeto, "Monto de Cotización", self.obj("barraestado")):
                    cantidad = self.obj("txt_md_01").get_text()
                    if len(cantidad) > 0:
                        monto = round(Decimal(cantidad) * Decimal(valor), 2)
                        self.obj("txt_md_03").set_text(str(monto))
                        self.comprobar_valor_monto(self.obj("txt_md_01"), monto)

            elif objeto == self.obj("txt_tj_00"):
                conexion = Op.conectar(self.datos_conexion)
                cursor = Op.consultar(conexion, "BancoRazonSocial, " +
                    "BancoNroDocumento, BancoTipoDocumento, BancoDireccion, " +
                    "BancoTelefono, idTitular, TitularRazonSocial, " +
                    "TitularNroDocumento, TitularTipoDocumento",
                    "tarjetas_s", " WHERE NroTarjeta = '" + valor + "'")
                datos = cursor.fetchall()
                cant = cursor.rowcount
                conexion.close()  # Finaliza la conexión

                if cant > 0:
                    direccion = "" if datos[0][3] is None else datos[0][3]
                    telefono = "" if datos[0][4] is None else datos[0][4]

                    self.obj("txt_tj_01_1").set_text(datos[0][0])
                    self.obj("txt_tj_01_2").set_text(datos[0][1])
                    self.obj("txt_tj_01_3").set_text(direccion)
                    self.obj("txt_tj_01_4").set_text(telefono)

                    # Asignación de Tipo de Documento (Banco) en Combo
                    model, i = self.obj("cmb_tj_banco").get_model(), 0
                    while model[i][0] != datos[0][2]: i += 1
                    self.obj("cmb_tj_banco").set_active(i)

                    self.obj("txt_tj_02").set_text(str(datos[0][5]))
                    self.obj("txt_tj_02_1").set_text(datos[0][6])
                    self.obj("txt_tj_02_2").set_text(datos[0][7])

                    # Asignación de Tipo de Documento (Titular) en Combo
                    model, i = self.obj("cmb_tj_titular").get_model(), 0
                    while model[i][0] != datos[0][8]: i += 1
                    self.obj("cmb_tj_titular").set_active(i)

                    self.obj("barraestado").push(0, "")
                    self.verificacion(0)
                else:
                    self.obj("btn_guardar_cobro").set_sensitive(False)
                    self.obj("txt_tj_00").grab_focus()
                    self.obj("barraestado").push(0, "La Tarjeta introducida no es válida (NO ESTÁ REGISTRADA).")

            elif objeto == self.obj("txt_tj_01"):
                if Op.comprobar_numero(int, objeto, "Cód. de Banco", self.obj("barraestado")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Banco", objeto, self.obj("txt_tj_01_1"),
                        self.obj("txt_tj_01_2"), self.obj("cmb_tj_banco"),
                        self.obj("txt_tj_01_3"), self.obj("txt_tj_01_4"))

            elif objeto == self.obj("txt_tj_01_2"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocBancoTarjeta + "'",
                    "Nro. de Documento del Banco", self.obj("txt_tj_01"),
                    self.obj("txt_tj_01_1"), objeto, self.obj("cmb_tj_banco"),
                    self.obj("txt_tj_01_3"), self.obj("txt_tj_01_4"))

            elif objeto == self.obj("txt_tj_02"):
                if Op.comprobar_numero(int, objeto, "Cód. de Titular", self.obj("barraestado")):
                    self.buscar_personas(objeto, "idPersona", valor,
                        "Cód. de Titular", objeto, self.obj("txt_tj_02_1"),
                        self.obj("txt_tj_02_2"), self.obj("cmb_tj_titular"))

            elif objeto == self.obj("txt_tj_02_2"):
                self.buscar_personas(objeto, "NroDocumento", "'" + valor + "'" +
                    " AND idTipoDocumento = '" + self.idTipoDocTitularTarjeta + "'",
                    "Nro. de Documento del Titular", self.obj("txt_tj_02"),
                    self.obj("txt_tj_02_1"), objeto, self.obj("cmb_tj_titular"))

            elif objeto == self.obj("txt_tj_03"):
                if Op.comprobar_numero(float, objeto, "Monto a Cobrar (Tarjeta)", self.obj("barraestado")):
                    self.comprobar_valor_monto(objeto, Decimal(valor))

    def buscar_personas(self, objeto, campo, valor, nombre, cod_per, rzn_scl, nro_doc, tip_doc, dir_per=None, tel_per=None):
        if dir_per is None:
            otros_campos = opcion = ""
        else:
            otros_campos = ", DireccionPrincipal, TelefonoPrincipal"
            opcion = " AND Empresa = 1"

        conexion = Op.conectar(self.datos_conexion)
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
            self.obj("btn_guardar_cobro").set_sensitive(False)
            objeto.grab_focus()
            self.obj("barraestado").push(0, "El " + nombre + " no es válido.")

            otro = nro_doc if objeto == cod_per else cod_per
            otro.set_text("")
            rzn_scl.set_text("")

            if dir_per is not None:
                dir_per.set_text("")
                tel_per.set_text("")

    def comprobar_valor_monto(self, objeto, valor):
        page = self.obj("notebook").get_current_page()
        if not self.editando_cobro:
            # Cuando Agrega un Nuevo Registro
            if valor <= self.monto_efectivo:
                if page == 0:
                    # Cheques de Terceros
                    self.comprobar_valor_cheque(valor)
                else:
                    # Tarjetas o Efectivo
                    self.obj("barraestado").push(0, "")
                    self.verificacion(0)
            else:
                objeto.grab_focus()
                self.obj("barraestado").push(0, "El Monto a Cobrar NO puede ser" +
                " mayor al monto disponible (" + str(self.monto_efectivo) + ").")
                self.obj("btn_guardar_cobro").set_sensitive(False)
        else:
            # Cuando Edita un Registro
            if page == 0:  # Cheques de Terceros
                disponible = self.monto_ch_doc + self.monto_efectivo
                if valor <= disponible:
                    self.comprobar_valor_cheque(valor)
                else:
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "El Monto a Cobrar NO puede ser " +
                    "mayor al monto disponible para ser asignado más el valor del " +
                    "Cheque (" + str(disponible) + ").")
                    self.obj("btn_guardar_cobro").set_sensitive(False)

            elif page == 1:  # Cobros en Efectivo
                disponible = self.monto_md_doc + self.monto_efectivo
                if valor <= disponible:
                    self.obj("barraestado").push(0, "")
                    self.verificacion(0)
                else:
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "El Monto a Cobrar NO puede ser mayor " +
                    "al monto disponible para ser asignado más el valor previamente " +
                    "asignado a este Cobro (" + str(disponible) + ").")
                    self.obj("btn_guardar_cobro").set_sensitive(False)

            else:  # Tarjetas
                disponible = self.monto_tj_doc + self.monto_efectivo
                if valor <= disponible:
                    self.obj("barraestado").push(0, "")
                    self.verificacion(0)
                else:
                    objeto.grab_focus()
                    self.obj("barraestado").push(0, "El Monto a Cobrar NO puede ser mayor " +
                    "al monto disponible para ser asignado más el valor previamente " +
                    "asignado a la Tarjeta (" + str(disponible) + ").")
                    self.obj("btn_guardar_cobro").set_sensitive(False)

##### Cheques ##########################################################

    def on_btn_cheque_clicked(self, objeto):
        self.txt_cod_ban, self.txt_scl_ban = self.obj("txt_ch_02"), self.obj("txt_ch_02_1")
        self.txt_doc_ban, self.cmb_doc_ban = self.obj("txt_ch_02_2"), self.obj("cmb_ch_banco")
        self.txt_dir_ban, self.txt_tel_ban = self.obj("txt_ch_02_3"), self.obj("txt_ch_02_4")

        self.txt_cod_tit, self.txt_scl_tit = self.obj("txt_ch_03"), self.obj("txt_ch_03_1")
        self.txt_doc_tit, self.cmb_doc_tit = self.obj("txt_ch_03_2"), self.obj("cmb_ch_titular")

        from clases.llamadas import chequeterceros
        chequeterceros(self.datos_conexion, self)

        self.obj("txt_ch_00").grab_focus()
        self.obj("barraestado").push(0, "")

    def on_btn_ch_banco_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_ch_02"), self.obj("txt_ch_02_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_ch_02_2"), self.obj("cmb_ch_banco")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_ch_02_3"), self.obj("txt_ch_02_4")
        self.obj("txt_ch_02").grab_focus()

        from clases.llamadas import personas
        personas(self.datos_conexion, self, "Empresa = 1")

    def on_btn_ch_titular_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_ch_03"), self.obj("txt_ch_03_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_ch_03_2"), self.obj("cmb_ch_titular")
        self.txt_dir_per = self.txt_tel_per = None
        self.obj("txt_ch_03").grab_focus()

        from clases.llamadas import personas
        personas(self.datos_conexion, self)

    def comprobar_valor_cheque(self, valor):
        if valor <= self.monto_cheque:
            self.obj("barraestado").push(0, "")
            self.verificacion(0)
        else:
            self.obj("txt_ch_04").grab_focus()
            self.obj("barraestado").push(0, "El Monto asignado NO puede" +
            " ser mayor al monto del Cheque (" + str(self.monto_cheque) + ").")
            self.obj("btn_guardar_cobro").set_sensitive(False)

##### Monedas ##########################################################

    def on_btn_moneda_clicked(self, objeto):
        from clases.llamadas import monedas
        monedas(self.datos_conexion, self)

        self.obj("txt_md_00").grab_focus()
        self.obj("barraestado").push(0, "")

##### Tarjetas #########################################################

    def on_btn_tarjeta_clicked(self, objeto):
        self.txt_cod_ban, self.txt_scl_ban = self.obj("txt_tj_01"), self.obj("txt_tj_01_1")
        self.txt_doc_ban, self.cmb_doc_ban = self.obj("txt_tj_01_2"), self.obj("cmb_tj_banco")
        self.txt_dir_ban, self.txt_tel_ban = self.obj("txt_tj_01_3"), self.obj("txt_tj_01_4")

        self.txt_cod_tit, self.txt_scl_tit = self.obj("txt_tj_02"), self.obj("txt_tj_02_1")
        self.txt_doc_tit, self.cmb_doc_tit = self.obj("txt_tj_02_2"), self.obj("cmb_tj_titular")

        from clases.llamadas import tarjetas
        tarjetas(self.datos_conexion, self)

        self.obj("txt_tj_00").grab_focus()
        self.obj("barraestado").push(0, "")

    def on_btn_tj_banco_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_tj_01"), self.obj("txt_tj_01_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_tj_01_2"), self.obj("cmb_tj_banco")
        self.txt_dir_per, self.txt_tel_per = self.obj("txt_tj_01_3"), self.obj("txt_tj_01_4")
        self.obj("txt_tj_01").grab_focus()

        from clases.llamadas import personas
        personas(self.datos_conexion, self, "Empresa = 1")

    def on_btn_tj_titular_clicked(self, objeto):
        self.txt_cod_per, self.txt_rzn_scl = self.obj("txt_tj_02"), self.obj("txt_tj_02_1")
        self.txt_nro_doc, self.cmb_tip_doc = self.obj("txt_tj_02_2"), self.obj("cmb_tj_titular")
        self.txt_dir_per = self.txt_tel_per = None
        self.obj("txt_tj_02").grab_focus()

        from clases.llamadas import personas
        personas(self.datos_conexion, self)
